import time

class MemoryStressTest:
    def __init__(self, target_mb=2000, chunk_mb=50):
        self.target_mb = target_mb
        self.chunk_mb = chunk_mb
        self.data = []

    def start(self):
        print(f"Reservando hasta {self.target_mb} MB...")
        allocated = 0

        try:
            while allocated < self.target_mb:
                # reserva bloques de memoria
                self.data.append(bytearray(self.chunk_mb * 1024 * 1024))
                allocated += self.chunk_mb

                print(f"Reservados: {allocated} MB")
                time.sleep(0.2)

            print("✅ Memoria saturada para pruebas")
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("Liberando memoria...")
            self.data.clear()


if __name__ == "__main__":
    stress = MemoryStressTest(target_mb=3000, chunk_mb=100)
    stress.start()