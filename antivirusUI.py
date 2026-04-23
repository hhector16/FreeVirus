import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox , QLineEdit , QPushButton , QLabel, QFrame, QStackedWidget, QPlainTextEdit, QScrollArea, QToolButton, QSizePolicy
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from UserInterfaceClases.Memory_widget import *
from UserInterfaceClases.CPU_usage_label import *
from UserInterfaceClases.Active_label import *
from UserInterfaceClases.HashTableWidget import *
from UserInterfaceClases.InstancesTableWidget import *
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp
import subprocess
import psutil



class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

class Image_label(QLabel):
    def __init__(self,x,min_malware,min_suspicious):
        super().__init__()
        self.setCursor(Qt.PointingHandCursor)
        self.id = x
        self.min_malware = min_malware
        self.min_suspicious = min_suspicious

    def seleccionar(self):
        global selected_image

        if selected_image is not None:
            selected_image.setStyleSheet("border: none;")

        try:
            with open("conf.json","r") as f:
                data = json.load(f)
            data["selected"] = self.id
            data["min_malware_score"] = self.min_malware
            data["min_suspicious_score"] = self.min_suspicious
            with open("conf.json","w") as f:
                json.dump(data,f,indent=4)
        except Exception as e:
            print("Error grave al cambiar configuración de protección, ",e)

        self.setStyleSheet("border: 3px solid blue;")
        selected_image = self
    



    def mousePressEvent(self, event):
        self.seleccionar()
            
class topbar(QWidget):
    def __init__(self,parent):
        super().__init__()
        self.setFixedHeight(40)
        self.parent_window = parent
        self.setStyleSheet("background-color: #262626;")
        
        self.close_button = QPushButton("X")
        self.close_button.clicked.connect(self.parent_window.close)    
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: none;
                border: none;
                color: red;
                font-weight: bold;
            }
            QPushButton:hover {
                color: white;  
            }
        """)
        self.close_button.setFixedSize(30, 30)
        
        self.min_button = QPushButton("-")
        self.min_button.clicked.connect(self.parent_window.showMinimized)
        self.min_button.setStyleSheet("""
            QPushButton {
                background-color: none;
                border: none;
                color: white;
                font-weight: bold;
                font-size: 20px;
            }
            QPushButton:hover {
                color: gray;  
            }
        """)
        self.min_button.setFixedSize(30, 30)
        topBar_layout=QHBoxLayout(self)
        topBar_layout.setAlignment(Qt.AlignRight)
        topBar_layout.setContentsMargins(0, 0, 10, 0)
        topBar_layout.setSpacing(0)
        bar1, bar2 = QLabel("|"), QLabel("|")
        bar1.setStyleSheet("background-color: none;")
        bar2.setStyleSheet("background-color: none;")
        topBar_layout.addWidget(bar1)
        topBar_layout.addWidget(self.min_button)
        topBar_layout.addWidget(bar2)
        topBar_layout.addWidget(self.close_button)  
        
    # Al presionar el mouse
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()  # guardamos posición inicial del mouse

    # Al mover el mouse mientras se mantiene presionado
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = event.globalPos() - self.oldPos  # calculamos desplazamiento
            self.parent_window.move(self.parent_window.x() + delta.x(),
                                        self.parent_window.y() + delta.y())  # movemos la ventana
            self.oldPos = event.globalPos()  # actualizamos posición

class rightContainer(QWidget):
    
    class IndexScreen(QWidget):
        def __init__(self):
            super().__init__()
            self.setStyleSheet("background-color: #3d3d3d;")  # gris claro
            self.layout=QVBoxLayout(self)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.setSpacing(0)
            self.layout.setAlignment(Qt.AlignTop)
            
            title = QLabel("Index")
            title.setStyleSheet("font-size: 24px; color: lightgreen; margin: 60px;")
            
            introduction = QLabel("Bienvenido a FreeVirus, nuestra aplicación dedicada al estudio y analisis del funcionamiento de los antivirus. Hemos desarrollado el software de un antivirus funcional como cualquier otro con la difrencia de que nos vamos a enfocar en explcicar su funcionamiento interno con fines educativos. Esta idea surgió ya que mediante mi proceso de investigación del funcionamiento de este tipo de software, era todo muy técnico y complejo para alguien sin conocimientos. Por ello, el objetivo de este TFG es desarrollar una aplicación con el fin de tratar de explicar visualmente su funcionamiento de forma que es más fácil de estudiarlo sin tener un conocimiento previo.")
            introduction.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 40px;") 
            introduction.setAlignment(Qt.AlignCenter)
            introduction.setWordWrap(True)
            
            introduction2 = QLabel("A la izquierda se encuentran botones con las diferentes secciones de la aplicación. Para observar el funcionamiento del antivirus sin poner en peligro su equipo, hemos creado un apartado de simulación en el que se muestran ejemplos de virus para comprobar el funcionamiento.")
            introduction2.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 40px;") 
            introduction2.setAlignment(Qt.AlignCenter)
            introduction2.setWordWrap(True)
            
            
            self.layout.addWidget(title, alignment=Qt.AlignHCenter)
            self.layout.addWidget(introduction)
            self.layout.addWidget(introduction2)
    
    class DashboardScreen(QWidget):
        def __init__(self):
            super().__init__()
            self.setStyleSheet("background-color: #3d3d3d;")  # gris claro
            self.layout=QVBoxLayout(self)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.setSpacing(0)
            self.layout.setAlignment(Qt.AlignTop)
            
            title = QLabel("Dashboard Screen")
            title.setStyleSheet("font-size: 24px; color: lightgreen; margin: 60px;")
            p1 = QLabel("The dashboard contains a summary of the antivirus, including two screens where you can see every fanotify detection and python analysis in real time including hash verification etc...")
            p1.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 40px;") 
            p1.setAlignment(Qt.AlignCenter)
            p1.setWordWrap(True)

            data = Active_label()

            self.layout.addWidget(title, alignment=Qt.AlignHCenter)
            self.layout.addWidget(p1)
            self.layout.addWidget(data,alignment=Qt.AlignHCenter)
            
    class ProtectionScreen(QWidget):

        

        def __init__(self):
            super().__init__()
            self.setStyleSheet("background-color: #3d3d3d;")  # gris claro
            self.layout=QVBoxLayout(self)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.setSpacing(0)
            self.layout.setAlignment(Qt.AlignTop)
                
            title = QLabel("Protection Screen")
            title.setStyleSheet("font-size: 24px; color: lightgreen; margin: 60px;")
            p1 = QLabel("In this screen you will be able to change the level of protection of the antivirus, changing this affects in how the antivirus reacts to unknown and suspicious files, the more protection addes the more secutirty but may block some harmless files resulting in false positives. By defect its in the intermediate level, where unknown files are treated as suspicious.")
            p1.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 40px;") 
            p1.setAlignment(Qt.AlignCenter)
            p1.setWordWrap(True)

            container1 = QWidget()
            container1.setStyleSheet("margin-top:10em;")
            container1_layout = QHBoxLayout(container1)

            # Imagen 1

            protectionImage1 = Image_label(1,40,70)
            pixmap1= QPixmap("images/av_rojo.png").scaled(int(200), int(200), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            protectionImage1.setPixmap(pixmap1)
            protectionImage1.setAlignment(Qt.AlignCenter)

            #Imagen 2

            protectionImage2 = Image_label(2,50,20)
            pixmap2= QPixmap("images/av_amarillo.png").scaled(int(200), int(200), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            protectionImage2.setPixmap(pixmap2)
            protectionImage2.setAlignment(Qt.AlignCenter)
            protectionImage2.seleccionar()

            # Imagen 3

            protectionImage3 = Image_label(3,30,15)
            pixmap3= QPixmap("images/av_verde.png").scaled(int(200), int(200), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            protectionImage3.setPixmap(pixmap3)
            protectionImage3.setAlignment(Qt.AlignCenter)

            container1_layout.addWidget(protectionImage1)
            container1_layout.addWidget(protectionImage2)
            container1_layout.addWidget(protectionImage3)
                
            self.layout.addWidget(title, alignment=Qt.AlignHCenter)
            self.layout.addWidget(p1)
            self.layout.addWidget(container1)
    
    class SimulationScreen(QWidget):
            
        class sim_index_screen(QWidget):
            cambiar_pantalla = pyqtSignal(int)
            def __init__(self):
                super().__init__()
                self.layout=QVBoxLayout(self)
                self.layout.setContentsMargins(0, 0, 0, 0)
                self.layout.setSpacing(0)
                self.layout.setAlignment(Qt.AlignTop)
                        
                title = QLabel("Simulation Screen")
                title.setStyleSheet("font-size: 24px; color: lightgreen; margin: 60px;")
                p1 = QLabel("In this section you will watch live all the process the antivirus engine follows in order to detect the virus including the analysis of the file,how its moved to quarantine and how the databases are updated. When you click the buton, the EICAR test will download explaining step by step the process. EICAR test is a harmless file that is used to test the functionality of antivirus software. It is detected as a virus by antivirus programs, but it does not contain any malicious code and does not pose any threat to your computer.")
                p1.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 40px;") 
                p1.setAlignment(Qt.AlignCenter)
                p1.setWordWrap(True)
                
                arrow_container = QWidget()
                arrow_layout = QHBoxLayout(arrow_container)
                
                right_btn = QToolButton()
                right_btn.setArrowType(Qt.RightArrow)
                
                right_btn.setIconSize(QSize(32, 32))
                
                right_btn.clicked.connect(lambda: self.cambiar_pantalla.emit(1))
                
                arrow_layout.addStretch()
                arrow_layout.addWidget(right_btn)

                options_container = QWidget()
                options_container_layout = QHBoxLayout(options_container)
                options_container_layout.setContentsMargins(0, 100, 0, 0)
                options_container_layout.setSpacing(60)


                Eicar_btn = QPushButton("EICAR")
                Eicar_btn.setFixedSize(200, 90)
                Eicar_btn.clicked.connect(lambda: self.cambiar_pantalla.emit(3))

                cpu_saturate_btm = QPushButton("Denial of service")
                cpu_saturate_btm.setFixedSize(200, 90)

                rsw_btn = QPushButton("virus 3")
                rsw_btn.setFixedSize(200, 90)

                options_container_layout.addWidget(Eicar_btn)
                options_container_layout.addWidget(cpu_saturate_btm)
                options_container_layout.addWidget(rsw_btn)

                options_description_container = QWidget()
                options_description_container.setStyleSheet("margin-top:50px;")

                options_description_container_layout = QHBoxLayout(options_description_container)

                Eicar_description = QLabel("This is a file created so all antivirus should detect this")
                Eicar_description.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 40px;") 
                Eicar_description.setAlignment(Qt.AlignCenter)
                Eicar_description.setWordWrap(True)

                cpu_saturate_description = QLabel("This is a DOS virus which overloads your cpu and ram")
                cpu_saturate_description.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 40px;") 
                cpu_saturate_description.setAlignment(Qt.AlignCenter)
                cpu_saturate_description.setWordWrap(True)

                rsw_description = QLabel("Ransomware which crypts your file so u cant see them")
                rsw_description.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 40px;") 
                rsw_description.setAlignment(Qt.AlignCenter)
                rsw_description.setWordWrap(True)

                options_description_container_layout.addWidget(Eicar_description)
                options_description_container_layout.addWidget(cpu_saturate_description)
                options_description_container_layout.addWidget(rsw_description)

                
                        
                self.layout.addWidget(title, alignment=Qt.AlignHCenter)
                self.layout.addWidget(p1)
                self.layout.addWidget(arrow_container)
                self.layout.addWidget(options_container)
                self.layout.addWidget(options_description_container)
            
        class sim_fanotify_screen(QWidget):
            cambiar_pantalla = pyqtSignal(int)
            def __init__(self):
                super().__init__()
                self.layout=QVBoxLayout(self)
                self.layout.setContentsMargins(0, 0, 0, 0)
                self.layout.setSpacing(0)
                self.layout.setAlignment(Qt.AlignTop)
                
                containerScroll = QWidget()
                layout = QVBoxLayout(containerScroll)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                layout.setAlignment(Qt.AlignTop)
                
                 # Para que sea scrolleable
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll.setWidget(containerScroll)
                        
                title = QLabel("Fanotify")
                title.setStyleSheet("font-size: 24px; color: lightgreen; margin: 60px;")
                p1 = QLabel("Basicly, every antivirus engine has a component that is responsible for monitoring the system in real time, watching for any file that is created, moved or executed. In our antivirus engine, this component is implemented using fanotify, a Linux kernel subsystem that provides file access notification and interception. Here is the function that intercepts executions:")
                p1.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 40px;") 
                p1.setAlignment(Qt.AlignCenter)
                p1.setWordWrap(True)
                
                code = '''
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
                            printf("[EXEC] %s", path);

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
                '''
                editor = QPlainTextEdit()
                editor.setPlainText(code)
                editor.setReadOnly(True)  # no editable
                editor.setFont(QFont("Courier New", 8))  # fuente monoespaciada
                editor.setMinimumHeight(300)
                editor.setStyleSheet("background-color: #2d2d2d; color: #f8f8f2; padding: 5px; border-radius: 6px; margin: 30px;")
                
                p2 = QLabel("To sum up this code, this structure 'struct fanotify_event_metadata *m;' contains all the information used later to store in the databases such as the pid and this condition 'if (m->mask & FAN_OPEN_EXEC_PERM)' means if somethings has executed, intercept it")                                                                                                                                                                
                p2.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 40px;") 
                p2.setAlignment(Qt.AlignCenter)
                p2.setWordWrap(True)
                
                arrow_container = QWidget()
                arrow_layout = QHBoxLayout(arrow_container)
                
                left_btn = QToolButton()
                left_btn.setArrowType(Qt.LeftArrow)

                right_btn = QToolButton()
                right_btn.setArrowType(Qt.RightArrow)
                
                left_btn.setIconSize(QSize(32, 32))
                right_btn.setIconSize(QSize(32, 32))
                
                left_btn.clicked.connect(lambda: self.cambiar_pantalla.emit(0))
                right_btn.clicked.connect(lambda: self.cambiar_pantalla.emit(2))
                
                arrow_layout.addWidget(left_btn)
                arrow_layout.addStretch()
                arrow_layout.addWidget(right_btn)
                                        
                layout.addWidget(title, alignment=Qt.AlignHCenter)
                layout.addWidget(p1)
                layout.addWidget(editor)
                layout.addWidget(p2)
                layout.addWidget(arrow_container)
                
                self.layout.addWidget(scroll)
            
        class sim_events_screen(QWidget):
            cambiar_pantalla = pyqtSignal(int)
            def __init__(self):
                super().__init__()
                self.layout=QVBoxLayout(self)
                self.layout.setContentsMargins(0, 0, 0, 0)
                self.layout.setSpacing(0)
                self.layout.setAlignment(Qt.AlignTop)
                
                title = QLabel("Events")
                title.setStyleSheet("font-size: 24px; color: lightgreen; margin: 60px;")
                p1 = QLabel("Here is a screen where you can see every event intercepted in eral time, with each type for example, [EXEC] corresponds to execution of a file. You can aslo see the path of the file that is executed. Look how the EICAR file is detected as it downloads")
                p1.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 40px;") 
                p1.setAlignment(Qt.AlignCenter)
                p1.setWordWrap(True)
                
                
                arrow_container = QWidget()
                arrow_layout = QHBoxLayout(arrow_container)
                
                left_btn = QToolButton()
                left_btn.setArrowType(Qt.LeftArrow)

                right_btn = QToolButton()
                right_btn.setArrowType(Qt.RightArrow)
                
                left_btn.setIconSize(QSize(32, 32))
                right_btn.setIconSize(QSize(32, 32))
                
                left_btn.clicked.connect(lambda: self.cambiar_pantalla.emit(1))
                right_btn.clicked.connect(lambda: self.cambiar_pantalla.emit(2))
                
                arrow_layout.addWidget(left_btn)
                arrow_layout.addStretch()
                arrow_layout.addWidget(right_btn)
                
                self.layout.addWidget(title, alignment=Qt.AlignHCenter)
                self.layout.addWidget(p1)
                self.layout.addWidget(arrow_container)

        class sim_eicar1_screen(QWidget):
            cambiar_pantalla = pyqtSignal(int)
            def __init__(self):
                super().__init__()
                self.layout=QVBoxLayout(self)
                self.layout.setContentsMargins(0, 0, 0, 0)
                self.layout.setSpacing(0)
                self.layout.setAlignment(Qt.AlignTop)
                
                what_is_eicar = QLabel()
                pixmap= QPixmap("images/what_is_eicar.png").scaled(int(500), int(500), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                what_is_eicar.setPixmap(pixmap)
                what_is_eicar.setAlignment(Qt.AlignCenter)

                what_is_eicar.setStyleSheet("margin-top:100px")

                title = QLabel("Events")
                title.setStyleSheet("font-size: 24px; color: lightgreen; margin: 60px;")
                p1 = QLabel("As we can see from 'https://procesia.com/test-antivirus-eicar-para-hackear-paginas-web/' its a file used to prove any antivirus. Next we are gonna execute this file so we check if our hash verify works properly. We will show you screenshots of how its detected and at the end you will try to execute it so you can see yourselves in the dashboard")
                p1.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 40px; margin-top:20px") 
                p1.setAlignment(Qt.AlignCenter)
                p1.setWordWrap(True)
                
                
                arrow_container = QWidget()
                arrow_layout = QHBoxLayout(arrow_container)

                
                

                right_btn = QToolButton()
                right_btn.setArrowType(Qt.RightArrow)
                
                right_btn.setIconSize(QSize(32, 32))
                
                right_btn.clicked.connect(lambda: self.cambiar_pantalla.emit(4))
                
                arrow_layout.addStretch()
                arrow_layout.addWidget(right_btn)
                
                self.layout.addWidget(what_is_eicar)
                self.layout.addWidget(p1)
                self.layout.addWidget(arrow_container)

        class sim_eicar2_screen(QWidget):
            cambiar_pantalla = pyqtSignal(int)
            def __init__(self):
                super().__init__()
                self.layout=QVBoxLayout(self)
                self.layout.setContentsMargins(0, 0, 0, 0)
                self.layout.setSpacing(0)
                self.layout.setAlignment(Qt.AlignTop)
                
                title = QLabel("How does EICAR look like?")
                title.setStyleSheet("font-size: 24px; color: lightgreen; margin: 60px;")
                p1 = QLabel("EICAR is a combination of random symbols designed to simulate a real virus signature, allowing antivirus programs to detect it safely without causing any actual harm to the system. ")
                p1.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 40px; margin-top:20px") 
                p1.setAlignment(Qt.AlignCenter)
                p1.setWordWrap(True)

                eicar_text = QLabel(r"X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*")
                eicar_text.setAlignment(Qt.AlignCenter)
                eicar_text.setStyleSheet("border: 1px solid black; margin-right:150px; margin-left:150px;margin-top:20px;margin-bottom:20px")         

                p2 = QLabel("When this virus downloads or this text is written down and saved, an event is thrown by fanotify and in that instance the antivirus engine calculates its hash, checks its veracity and stores it in our databases. ")
                p2.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 40px; margin-top:20px") 
                p2.setAlignment(Qt.AlignCenter)
                p2.setWordWrap(True)       
                
                eicar_database = QLabel()
                pixmap= QPixmap("images/eicar_database.png").scaled(int(500), int(500), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                eicar_database.setPixmap(pixmap)
                eicar_database.setAlignment(Qt.AlignCenter)
                eicar_database.setStyleSheet("margin-top:50px;")


                arrow_container = QWidget()
                arrow_layout = QHBoxLayout(arrow_container)

                left_btn = QToolButton()
                left_btn.setArrowType(Qt.LeftArrow)

                right_btn = QToolButton()
                right_btn.setArrowType(Qt.RightArrow)
                
                right_btn.setIconSize(QSize(32, 32))
                left_btn.setIconSize(QSize(32, 32))
                
                left_btn.clicked.connect(lambda: self.cambiar_pantalla.emit(3))
                right_btn.clicked.connect(lambda: self.cambiar_pantalla.emit(5))
                
                arrow_layout.addWidget(left_btn)
                arrow_layout.addStretch()
                arrow_layout.addWidget(right_btn)
                
                self.layout.addWidget(title, alignment=Qt.AlignHCenter)
                self.layout.addWidget(p1)
                self.layout.addWidget(eicar_text)
                self.layout.addWidget(p2)
                self.layout.addWidget(eicar_database)
                self.layout.addWidget(arrow_container)
            
        class sim_eicar3_screen(QWidget):
            cambiar_pantalla = pyqtSignal(int)
            def __init__(self):
                super().__init__()
                self.layout=QVBoxLayout(self)
                self.layout.setContentsMargins(0, 0, 0, 0)
                self.layout.setSpacing(0)
                self.layout.setAlignment(Qt.AlignTop)
                
                title = QLabel("How we check its veracity?")
                title.setStyleSheet("font-size: 24px; color: lightgreen; margin: 60px;")

                p1 = QLabel("When we calculate its hash we make a call to VirusTotalAPI where it compares it with their database and returns some suspicious socres. We also calculate its entriopy which means how dispair the text form the file is. This way we implement the hash verification which is one of the most imporant measures as it checks if the virus has been detected before")
                p1.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 40px; margin-top:20px") 
                p1.setAlignment(Qt.AlignCenter)
                p1.setWordWrap(True)


                Eicar_btn = QPushButton("EICAR")
                Eicar_btn.setFixedSize(200, 90)
                Eicar_btn.clicked.connect(lambda: self.cambiar_pantalla.emit(3))

                p2 = QLabel("This button will download EICAR so you can see it yourselve in the database and the dashboard!!")
                p2.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 40px; margin-top:20px") 
                p2.setAlignment(Qt.AlignCenter)
                p2.setWordWrap(True)

                arrow_container = QWidget()
                arrow_layout = QHBoxLayout(arrow_container)

                left_btn = QToolButton()
                left_btn.setArrowType(Qt.LeftArrow)

                right_btn = QToolButton()
                right_btn.setArrowType(Qt.RightArrow)
                
                right_btn.setIconSize(QSize(32, 32))
                left_btn.setIconSize(QSize(32, 32))
                
                left_btn.clicked.connect(lambda: self.cambiar_pantalla.emit(4))
                
                arrow_layout.addWidget(left_btn)
                arrow_layout.addStretch()
                
                self.layout.addWidget(title, alignment=Qt.AlignHCenter)
                self.layout.addWidget(p1)
                self.layout.addWidget(Eicar_btn, alignment=Qt.AlignHCenter)
                self.layout.addWidget(p2)
                self.layout.addWidget(arrow_container)

                
                
        # SimulationScreen, pantalla padre de las subpantallas de simulación        
        def __init__(self):
            super().__init__()
            self.setStyleSheet("background-color: #3d3d3d;")  # gris claro
                            
            self.stack = QStackedWidget()
            
            # Layout
                
            self.layout=QVBoxLayout(self)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.setSpacing(0)
            
            # Crear subpantallas
                
            index = self.sim_index_screen()
            index.cambiar_pantalla.connect(self.stack.setCurrentIndex)

            fanotify = self.sim_fanotify_screen()
            fanotify.cambiar_pantalla.connect(self.stack.setCurrentIndex)

            events = self.sim_events_screen()
            events.cambiar_pantalla.connect(self.stack.setCurrentIndex)

            eicar1 = self.sim_eicar1_screen()
            eicar1.cambiar_pantalla.connect(self.stack.setCurrentIndex)

            eicar2 = self.sim_eicar2_screen()
            eicar2.cambiar_pantalla.connect(self.stack.setCurrentIndex)

            eicar3 = self.sim_eicar3_screen()
            eicar3.cambiar_pantalla.connect(self.stack.setCurrentIndex)

            # Añadir subpantallas al stack
                
            self.stack.addWidget(index)
            self.stack.addWidget(fanotify)
            self.stack.addWidget(events)
            self.stack.addWidget(eicar1)
            self.stack.addWidget(eicar2)
            self.stack.addWidget(eicar3)

            self.stack.setCurrentIndex(0)
            
            self.layout.addWidget(self.stack)
            
    class CPUScreen(QWidget):
        def __init__(self):
            super().__init__()
            self.setStyleSheet("background-color: #3d3d3d;")  # gris claro
            self.layout=QVBoxLayout(self)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.setSpacing(0)
            self.layout.setAlignment(Qt.AlignTop)
                
            title = QLabel("CPU usage ")
            title.setStyleSheet("font-size: 24px; color: lightgreen; margin: 60px;")
            p1 = QLabel("Being aware of your CPU usage is important because it allows you to understand how your system resources are being used and prevent performance issues.")
            p1.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 40px;") 
            p1.setAlignment(Qt.AlignCenter)
            p1.setWordWrap(True)

            memory = Memory_widget()

            p2 = QLabel(str(psutil.cpu_percent()))
            p2.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 40px;") 
            p2.setAlignment(Qt.AlignCenter)
            p2.setWordWrap(True)

            cpu_label = CPU_usage_label()
                
            self.layout.addWidget(title, alignment=Qt.AlignHCenter)
            self.layout.addWidget(p1)
            self.layout.addWidget(memory)
            self.layout.addWidget(cpu_label)
            
    class dataBasesScreen(QWidget):
        def __init__(self):
            super().__init__()
            self.setStyleSheet("background-color: #3d3d3d;")  # gris claro
            self.layout=QVBoxLayout(self)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.setSpacing(0)
            self.layout.setAlignment(Qt.AlignTop)
                
            title = QLabel("DataBases Screen")
            title.setStyleSheet("font-size: 24px; color: lightgreen; margin: 60px;")
            p1 = QLabel("In this section you will be able to check out the state of both databases, the one with each hash and the databse with the instances of each executable. Thius databases are updated in real time if the antivirus engine is running.")
            p1.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 40px; margin-bottom:40px;") 
            p1.setAlignment(Qt.AlignCenter)
            p1.setWordWrap(True)

            p2 = QLabel("Hashes database")
            p2.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 40px; margin-bottom:40px;") 
            p2.setAlignment(Qt.AlignCenter)
            p2.setWordWrap(True)

            p3 = QLabel("Instances database")
            p3.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 40px; margin-bottom:40px;") 
            p3.setAlignment(Qt.AlignCenter)
            p3.setWordWrap(True)

            tabla = HashTableWidget()
            instancesTable = InstancesTableWidget()
                
            self.layout.addWidget(title, alignment=Qt.AlignHCenter)
            self.layout.addWidget(p1)
            self.layout.addWidget(p2)
            self.layout.addWidget(tabla, alignment=Qt.AlignHCenter)
            self.layout.addWidget(p3)
            self.layout.addWidget(instancesTable, alignment=Qt.AlignHCenter)


            
    class FirewallScreen(QWidget):
        def __init__(self):
            super().__init__()
            self.setStyleSheet("background-color: #3d3d3d;")  # gris claro
            self.layout=QVBoxLayout(self)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.setSpacing(0)
            self.layout.setAlignment(Qt.AlignTop)
                
            title = QLabel("Firewall Screen")
            title.setStyleSheet("font-size: 24px; color: lightgreen; margin: 60px;")

            p1 = QLabel("A firewall is a layer between your computer and the connections arriving or outgoing. Here we will show active nftables rules which decide which traffic is allowed to come or go and you will be able to add or delete more of this rules")
            p1.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 40px; margin-bottom:40px;") 
            p1.setWordWrap(True)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            self.iptablesLabel = QLabel()
            self.iptablesLabel.setStyleSheet("border:1 solid gray;color:black;text-align:center")
            self.iptablesLabel.setAlignment(Qt.AlignTop)
            self.iptablesLabel.setMinimumWidth(500)
            scroll.setWidget(self.iptablesLabel)

            comando = ["iptables", "-L", "-v", "-n"]

            try:
                # Ejecuta el comando y captura la salida
                resultado = subprocess.run(
                    comando,
                    capture_output=True,  # Captura stdout y stderr
                    text=True,            # Devuelve strings en lugar de bytes
                    check=True            # Lanza excepción si hay error
                )

                # Muestra la salida
                iptables = resultado.stdout
                self.iptablesLabel.setText(iptables)

            except subprocess.CalledProcessError as e:
                print("Ocurrió un error al ejecutar el comando:")
                print(e.stderr)

            rules_container = QWidget()
            rules_container_layout = QHBoxLayout(rules_container)

            p2 = QLabel("Set rule")     
            p2.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 40px;") 
            p2.setWordWrap(True)

            p8 = QLabel("Operation:")     
            p8.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 40px; margin-right: 10px; margin-bottom:40px;margin-top:40px") 
            p8.setWordWrap(True)
                
            self.selectOperation = QComboBox()
            self.selectOperation.addItems(["INSERT","APPEND","DELETE"])

            self.selectOperation.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            self.selectOperation.setFixedWidth(90)

            p3 = QLabel("Rule type:")     
            p3.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 10px; margin-right: 10px; margin-bottom:40px;margin-top:40px") 
            p3.setWordWrap(True)
                
            self.select = QComboBox()
            self.select.addItems(["INPUT","OUTPUT","FORDWARD"])
            self.select.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            self.select.setFixedWidth(110)

            p4 = QLabel("Protocol:")     
            p4.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 10px; margin-right: 10px; margin-bottom:40px;margin-top:40px") 
            p4.setWordWrap(True)

            self.protocolSelect = QComboBox()
            self.protocolSelect.addItems(["tcp","udp"])
            self.protocolSelect.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

            p5 = QLabel("Ports:")     
            p5.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 10px; margin-right: 10px; margin-bottom:40px;margin-top:40px") 
            p5.setWordWrap(True)

            self.portsInput = QLineEdit()
            self.portsInput.setFixedWidth(80)

            p6 = QLabel("Block ip (optional):")     
            p6.setStyleSheet("font-size: 16px; color: darkgray; margin-left: 10px; margin-right: 10px; margin-bottom:40px;margin-top:40px") 
            p6.setWordWrap(True)

            self.ipsInput = QLineEdit()
            ip_regex = QRegExp(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
            ip_validator = QRegExpValidator(ip_regex)
            self.ipsInput.setValidator(ip_validator)
            self.ipsInput.setPlaceholderText("192.168.1.120")

            self.do = QComboBox()
            self.do.addItems(["ACCEPT","DROP"])
            self.do.setFixedWidth(80)

            add_rule_button = QPushButton("Add rule")
            add_rule_button.setStyleSheet("margin-right:50px;")
            add_rule_button.clicked.connect(self.setRule)

            p7 = QLabel("Note: for it to work properly, you first need to make sure that the iptables are activated. If there is any mistake in the indroduced ip or ports, the rule wont be added ")     
            p7.setStyleSheet("font-size: 14px; color: darkgray; margin-left: 40px; margin-right: 10px; margin-bottom:40px;margin-top:40px") 
            p7.setWordWrap(True)



            self.layout.addWidget(title, alignment=Qt.AlignHCenter)
            self.layout.addWidget(p1)
            self.layout.addWidget(scroll, alignment=Qt.AlignHCenter)

            rules_container_layout.addWidget(p8)
            rules_container_layout.addWidget(self.selectOperation)
            rules_container_layout.addWidget(p3)
            rules_container_layout.addWidget(self.select)
            rules_container_layout.addWidget(p4)
            rules_container_layout.addWidget(self.protocolSelect)
            rules_container_layout.addWidget(p5)
            rules_container_layout.addWidget(self.portsInput)
            rules_container_layout.addWidget(p6)
            rules_container_layout.addWidget(self.ipsInput)
            rules_container_layout.addWidget(self.do)
            rules_container_layout.addWidget(add_rule_button)

            self.layout.addWidget(rules_container)
            self.layout.addWidget(p7)

        def setRule(self):
            ips = self.ipsInput.text()
            ports = self.portsInput.text()
            operation = self.selectOperation.currentText()
            select = self.select.currentText()
            protocol = self.protocolSelect.currentText()
            do = self.do.currentText()

            if operation == "INSERT":
                operation = "-I"
            elif operation == "APPEND":
                operation == "-A"
            elif operation == "DELETE":
                operation = "-D"

            self.ipsInput.setText("")
            self.portsInput.setText("")

            if(ips == ""):
                comando = ["iptables",operation,select,"-p",protocol,"--dport",ports,"-j",do]
            else:
                comando = ["iptables",operation,select,"-p",protocol,"--dport",ports,"-s",ips,"-j",do]
            try:
                # Ejecuta el comando y captura la salida
                resultado = subprocess.run(
                    comando,
                    capture_output=True,  # Captura stdout y stderr
                    text=True,            # Devuelve strings en lugar de bytes
                    check=True            # Lanza excepción si hay error
                )

                # Muestra la salida
                iptables = resultado.stdout
            except subprocess.CalledProcessError as e:
                print("Ocurrió un error al ejecutar el comando:")
                print(e.stderr)

            comando = ["iptables", "-L", "-v", "-n"]
            try:
                # Ejecuta el comando y captura la salida
                resultado = subprocess.run(
                    comando,
                    capture_output=True,  # Captura stdout y stderr
                    text=True,            # Devuelve strings en lugar de bytes
                    check=True            # Lanza excepción si hay error
                )

                # Muestra la salida
                iptables = resultado.stdout
                self.iptablesLabel.setText(iptables)

            except subprocess.CalledProcessError as e:
                print("Ocurrió un error al ejecutar el comando:")
                print(e.stderr)


            
    class SettingsScreen(QWidget):
        def __init__(self):
            super().__init__()
            self.setStyleSheet("background-color: #3d3d3d;")  # gris claro
            self.layout=QVBoxLayout(self)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.setSpacing(0)
            self.layout.setAlignment(Qt.AlignTop)
                
            title = QLabel("Settings Screen")
            title.setStyleSheet("font-size: 24px; color: lightgreen; margin: 60px;")
                
            self.layout.addWidget(title, alignment=Qt.AlignHCenter)
        
    def __init__(self): 
        super().__init__()
        self.setStyleSheet("background-color: #3d3d3d;")  # gris claro
        self.stack = QStackedWidget()
        
        # Layout
        
        self.layout=QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Definir pantallas
        
        index = self.IndexScreen()
        dashboard = self.DashboardScreen()
        protection = self.ProtectionScreen()
        cpu = self.CPUScreen()
        simulation = self.SimulationScreen()
        dataBases = self.dataBasesScreen()
        firewall = self.FirewallScreen()
        settings = self.SettingsScreen()

        # Añadir pantallas al stack
        
        self.stack.addWidget(index)
        self.stack.addWidget(dashboard)
        self.stack.addWidget(protection)
        self.stack.addWidget(cpu)
        self.stack.addWidget(simulation)
        self.stack.addWidget(dataBases)
        self.stack.addWidget(firewall)
        self.stack.addWidget(settings)
        
        self.stack.setCurrentWidget(index)
        
        # Añadir  al layout
        
        self.layout.addWidget(self.stack)
        
        
class VentanaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FreeVirus ")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.oldPos = self.pos()
        # Fondo gris oscuro usando stylesheet
        self.setStyleSheet("background-color: #2b2b2b;")  # gris oscuro
        ancho = int(0.8 * QApplication.primaryScreen().size().width())
        alto = int(0.8 * QApplication.primaryScreen().size().height()) 
        self.resize(ancho, alto)
        self.maximumWidth = ancho
        self.maximumHeight = alto
        
        
        
        # Definimos widgets
        
        # TOPBAR
        topBar = topbar(self)
        
        # Main container
        
        main_container = QWidget()
        main_container.setStyleSheet("background-color: blue;")  # gris oscuro
        main_container.setMinimumHeight(alto - topBar.height())
        
        # Left container
        
        dashboard = ClickableLabel("Dashboard")
        protection = ClickableLabel("Protection")
        cpu = ClickableLabel("CPU usage")
        simulationl = ClickableLabel("Simulation")
        dataBases = ClickableLabel("DataBases")
        firewall = ClickableLabel("Firewall")
        settings = ClickableLabel("Settings")

        #Definirmos labels


        buttons = [dashboard, protection, cpu, simulationl, dataBases, firewall, settings]

        def clear_styles():
            for btn in buttons:
                if btn == dashboard:
                    btn.setStyleSheet("font-weight: bold;color: darkgray;margin-top: 20px;")
                else:
                    btn.setStyleSheet("font-weight: bold;color: darkgray;")
        left_container = QWidget()
        left_container.setStyleSheet("background-color: #333333;")  # gris medio
        left_container.setFixedWidth(int(ancho * 0.25))
        left_container.setFixedHeight(alto - topBar.height())
        
        logo_img = QLabel()
        pixmap = QPixmap("images/logo.png").scaled(int(ancho * 0.2), int(alto * 0.2), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_img.setPixmap(pixmap)
        logo_img.setAlignment(Qt.AlignCenter)
        logo_img.setMargin(30)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)   # Línea horizontal
        line.setFrameShadow(QFrame.Sunken) # Sombra para efecto 3D
        line.setStyleSheet("color: gray; margin-top: 20px; margin-bottom: 20px;")
        
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)   # Línea horizontal
        line2.setFrameShadow(QFrame.Sunken) # Sombra para efecto 3D
        line2.setStyleSheet("color: gray; margin-top: 20%; margin-bottom: 20px;")

        dashboard.setStyleSheet("font-weight: bold;color: darkgray;margin-top: 20px; ")
        dashboard.clicked.connect(lambda: (right_container.stack.setCurrentIndex(1),clear_styles(), dashboard.setStyleSheet("color: lightgreen; font-weight: bold;margin-top: 20px; ")))
        dashboard.setMargin(20)
        
        protection.clicked.connect(lambda: (right_container.stack.setCurrentIndex(2),clear_styles(), protection.setStyleSheet("color: lightgreen; font-weight: bold; ")))
        protection.setMargin(20)
        protection.setStyleSheet("font-weight: bold;color: darkgray;")

        cpu.clicked.connect(lambda: (right_container.stack.setCurrentIndex(3),clear_styles(), cpu.setStyleSheet("color: lightgreen; font-weight: bold; ")))
        cpu.setMargin(20)
        cpu.setStyleSheet("font-weight: bold;color: darkgray;")

        simulationl.clicked.connect(lambda: (right_container.stack.setCurrentIndex(4),clear_styles(), simulationl.setStyleSheet("color: lightgreen; font-weight: bold; "),right_container.stack.widget(4).stack.setCurrentIndex(0)))
        simulationl.setMargin(20)
        simulationl.setStyleSheet("font-weight: bold;color: darkgray;")
        
        dataBases.clicked.connect(lambda: (right_container.stack.setCurrentIndex(5),clear_styles(), dataBases.setStyleSheet("color: lightgreen; font-weight: bold; ")))
        dataBases.setMargin(20)
        dataBases.setStyleSheet("font-weight: bold;color: darkgray;")
        
        firewall.clicked.connect(lambda: (right_container.stack.setCurrentIndex(6),clear_styles(), firewall.setStyleSheet("color: lightgreen; font-weight: bold;")))
        firewall.setMargin(20)
        firewall.setStyleSheet("font-weight: bold;color: darkgray;")  
        
        settings.clicked.connect(lambda: (right_container.stack.setCurrentIndex(7),clear_styles(), settings.setStyleSheet("color: lightgreen; font-weight: bold; ")))
        settings.setMargin(20)
        settings.setStyleSheet("font-weight: bold;color: darkgray;")
        
        #Right container
        
        right_container = rightContainer()
        
        # Layouts
        
        main_layout=QVBoxLayout(self)
        main_container_layout=QHBoxLayout(main_container)
        left_container_layout=QVBoxLayout(left_container)
        
        # Añadir widgets a los layouts
        
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.addWidget(topBar)
        main_layout.addWidget(main_container)
       
        main_container_layout.setContentsMargins(0, 0, 0, 0)
        main_container_layout.setSpacing(0)
        main_container_layout.addWidget(left_container)
        main_container_layout.addWidget(right_container)
        
        left_container_layout.setContentsMargins(0, 0, 0, 0)
        left_container_layout.setAlignment(Qt.AlignTop)
        left_container_layout.setSpacing(0)
        left_container_layout.addWidget(logo_img, alignment=Qt.AlignHCenter)
        left_container_layout.addWidget(line)
        left_container_layout.addWidget(dashboard, alignment=Qt.AlignHCenter)
        left_container_layout.addWidget(protection, alignment=Qt.AlignHCenter)
        left_container_layout.addWidget(simulationl, alignment=Qt.AlignHCenter)
        left_container_layout.addWidget(cpu, alignment=Qt.AlignHCenter)
        left_container_layout.addWidget(dataBases, alignment=Qt.AlignHCenter)
        left_container_layout.addWidget(firewall, alignment=Qt.AlignHCenter)
        left_container_layout.addWidget(line2)
        left_container_layout.addWidget(settings, alignment=Qt.AlignHCenter)

selected = 2
selected_image = None

def check_selected():
    global selected
    try:
        with open ("conf.json","r") as f:
            conf = json.load(f)
            selected = conf["selected"]
    except:
        print("Error con el JSON")
        selected = 2

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())