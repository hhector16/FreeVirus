#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <limits.h>
#include <string.h>
#include <errno.h>
#include <poll.h>
#include <sys/fanotify.h>
#include <sys/socket.h>
#include <sys/un.h>

#define RUTA_SOCKET "/tmp/av.sock"
#define BUF_LEN 8192

// Estructura auxiliar para pasar datos a python
#pragma pack(push, 1)
typedef struct {
    pid_t pid;
    pid_t ppid;
    uint64_t event;     // m->mask
    char path[PATH_MAX];
} paquete;
#pragma pack(pop)

/*
    struct sockaddr_un {
        sa_family_t sun_family;  AF_UNIX
        char        sun_path[108]; 
    };

    struct fanotify_event_metadata {
        __u32 event_len;        Tamaño total del evento 
        __u8  vers;             Versión de la estructura 
        __u8  reserved;         Reservado 
        __u16 metadata_len;     Tamaño de los metadatos 
        __aligned_u64 mask;     Máscara de eventos (FAN_OPEN, FAN_CLOSE_WRITE, etc.)
        __s32 fd;               File descriptor del archivo afectado
        __s32 pid;              PID del proceso que causó el evento
    };
*/

// Método prara enviar datos a python y que este decida si bloquear o permitir la operación
// El argumento es la riuta del archivo a analizar
// Devuelve 1 para denegar, 0 para permitir

pid_t get_ppid_from_pid(pid_t pid) {
    char path[64];
    char buf[1024];
    snprintf(path, sizeof(path), "/proc/%d/stat", pid);

    FILE *f = fopen(path, "r");
    if (!f)
        return -1;

    pid_t ppid;
    /*
       Formato:
       pid (comm) state ppid ...
       El segundo campo puede tener espacios → hay que saltarlo bien
    */
    fscanf(f, "%*d (%*[^)]) %*c %d", &ppid);
    fclose(f);

    return ppid;
}


int ask_python(const char *path, pid_t pid, pid_t ppid, uint64_t event) {
    int sock;
    struct sockaddr_un addr;
    char response[16] = {0};    // Mejor inicializar a 0
    paquete paquete = {0};

    paquete.pid = pid;
    paquete.ppid = ppid;
    paquete.event = event;
    strncpy(paquete.path, path, PATH_MAX-1);
    paquete.path[PATH_MAX - 1] = '\0';          

    sock = socket(AF_UNIX, SOCK_STREAM, 0);
    if (sock < 0)
        return 0;

    memset(&addr, 0, sizeof(addr)); 
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, RUTA_SOCKET, sizeof(addr.sun_path) - 1);

    if (connect(sock, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        close(sock);
        return 0;   
    }

    write(sock, &paquete, sizeof(paquete));
    read(sock, response, sizeof(response) - 1);

    close(sock);

    return (strncmp(response, "DENY", 4) == 0);
}


// Función para obtener la ruta del archivo a partir de su file descriptor
void get_path(int fd, char *buf, size_t size) {
    char fdpath[64];
    char tmp[PATH_MAX];
    snprintf(fdpath, sizeof(fdpath), "/proc/self/fd/%d", fd);
    ssize_t r = readlink(fdpath, tmp, sizeof(tmp) - 1);
    if (r > 0) {
        tmp[r] = 0;
        if (!realpath(tmp, buf)) {  // convierte a ruta absoluta
            strncpy(buf, tmp, size - 1);
            buf[size - 1] = 0;
        }
    } else {
        strncpy(buf, "unknown", size - 1);
        buf[size - 1] = 0;
    }
}

// Función para cuando se detecta una descarga de archivo
/*void handle_download(int fan_fd) {
    char buffer[BUF_LEN];
    ssize_t len = read(fan_fd, buffer, sizeof(buffer));
    if (len <= 0)
        return;

    struct fanotify_event_metadata *m;

    for (m = (struct fanotify_event_metadata *)buffer;
         FAN_EVENT_OK(m, len);
         m = FAN_EVENT_NEXT(m, len)) {

        if (m->mask & FAN_CLOSE_WRITE) {

            char path[PATH_MAX];
            get_path(m->fd, path, sizeof(path));

            printf("[DOWNLOAD] %s\n", path);

            // análisis post-descarga 
            ask_python(path,m->pid);
        }

        close(m->fd);
    }
}*/

// Función para cuando se deteta una ejecución de archivo
void handle_exec(int fan_fd) {
    char buffer[BUF_LEN];
    ssize_t len = read(fan_fd, buffer, sizeof(buffer));
    if (len <= 0)
        return;

    struct fanotify_event_metadata *m;

    for (m = (struct fanotify_event_metadata *)buffer;
         FAN_EVENT_OK(m, len);
         m = FAN_EVENT_NEXT(m, len)) {

        if (m->vers != FANOTIFY_METADATA_VERSION)
            continue;

        if (m->mask & FAN_OPEN_EXEC_PERM) {

            char path[PATH_MAX];
            get_path(m->fd, path, sizeof(path));
            pid_t ppid = get_ppid_from_pid(m->pid);
            uint64_t event = m->mask;
            printf("[EXEC] %s\n", path);

            int deny = ask_python(path,m->pid,ppid,event);

            struct fanotify_response resp = {
                .fd = m->fd,
                .response = deny ? FAN_DENY : FAN_ALLOW
            };

            write(fan_fd, &resp, sizeof(resp));
        }

        close(m->fd);
    }
}

int main() {

    //int fan_download;
    int fan_exec;

    /*fan_download = fanotify_init(
        FAN_CLASS_NOTIF | FAN_NONBLOCK | FAN_CLOEXEC,
        O_RDONLY | O_LARGEFILE
    );*/

    fan_exec = fanotify_init(
        FAN_CLASS_PRE_CONTENT | FAN_CLOEXEC,
        O_RDONLY | O_LARGEFILE
    );

    if (/*fan_download < 0 || */fan_exec < 0) {
        perror("fanotify_init");
        exit(1);
    }

    /*fanotify_mark(
        fan_download,
        FAN_MARK_ADD | FAN_MARK_MOUNT,
        FAN_CLOSE_WRITE,
        AT_FDCWD,
        "/"
    );*/

    fanotify_mark(
        fan_exec,
        FAN_MARK_ADD | FAN_MARK_MOUNT,
        FAN_OPEN_EXEC_PERM,
        AT_FDCWD,
        "/"
    );

    struct pollfd fds[2];

    /*fds[0].fd = fan_download;
    fds[0].events = POLLIN;*/

    fds[1].fd = fan_exec;
    fds[1].events = POLLIN;

    printf("Fanotify activado\n");

    while (1) {

        poll(fds, 2, -1);

        /*if (fds[0].revents & POLLIN)
            handle_download(fan_download);*/

        if (fds[1].revents & POLLIN)
            handle_exec(fan_exec);
    }
}
