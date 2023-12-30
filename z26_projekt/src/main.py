import tcp_server
import udp_server
import logger

if __name__ == "__main__":
    tcp_server.start()
    udp_server.start()

    logger.info("All services started")
