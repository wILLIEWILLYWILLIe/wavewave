import base64
import json
from enum import StrEnum
from io import BytesIO

from mqtt_client import MqttPublisher
from targets_fig_maker import TargetFigMaker  # Uncomment if you have this file


class MessageLevel(StrEnum):
    info = "info"
    debug = "debug"
    warning = "warning"
    error = "error"


class MqttDebugger:
    '''
    A tool that can upload debugging messages or images to MQTT broker.
    By defualt, the broker is host itself. Users can sepcify a desired broker in the argument.
    '''
    TOPIC_MESSAGE = "message"
    TOPIC_RADAR = "radar"
    TOPIC_SPECTROGRAM = "spec"
    TOPIC_ANTENNA = "ant"
    TOPIC_PF = "pf"
    TOPIC_TARGET = "target"
    TOPIC_SIMULATE = "simulate"

    def __init__(self, broker="127.0.0.1", port=1884, verbose=False):
        '''
        verbose: print uploaded messages or not
        '''
        self.__verbose = verbose
        self.__publisher = MqttPublisher(broker, port)
        # clear exist radar and simulate data if shown
        self.send_simulate([], [], [])
        self.send_radar([], [], [], [])
        self.__target_fig_maker = TargetFigMaker()  # Uncomment if you have this file

    def __del__(self):
        self.__publisher.stop()

    def send(self, topic: str, text: str):
        '''
        Send a debugging message to MQTT broker.
        ### Args
        - topic(str): MQTT topic
        - text(str): the message to be sent
        '''
        self.__publisher.publish(topic, text)

    def send_radar(self, id_list: list[str], azm_list: list[float],
                   elv_list: list[float], color_list: list[str]):
        '''
        A convinent function to send radar data.
        '''
        self.send(topic=self.TOPIC_RADAR,
                  text=json.dumps({
                      "id": id_list,
                      "azm": azm_list,
                      "elv": elv_list,
                      "color": color_list
                  }))
        if self.__verbose:
            print(
                f"Published radar data: id={id_list}, azm={azm_list}, elv={elv_list}"
            )

    def send_simulate(self, id_list: list[str], azm_list: list[float],
                      elv_list: list[float]):
        '''
        A convinent function to send simulate data.
        '''
        self.send(topic=self.TOPIC_SIMULATE,
                  text=json.dumps({
                      "id": id_list,
                      "azm": azm_list,
                      "elv": elv_list
                  }))
        if self.__verbose:
            print(
                f"Published simulate data: id={id_list}, azm={azm_list}, elv={elv_list}"
            )

    def send_targets(self, stt_info: dict, ltt_info: dict, fl_mhz: int,
                     fh_mhz: int, bw_mhz: int):
        '''
        A convinent function to send targets data.
        '''
        # save figure to BytesIO
        buf = BytesIO()
        self.__target_fig_maker.make(stt_info, ltt_info, buf, fl_mhz, fh_mhz,
                                     bw_mhz)
        buf.seek(0)

        # encode to base64
        fig = base64.b64encode(buf.read()).decode('utf-8')
        self.send(topic=self.TOPIC_TARGET, text=json.dumps({"fig": fig}))

    def send_spectrogram(self, fig: bytes):
        '''
        A convinent function to send spectrogram.
        ### Args
        - topic(str): MQTT topic
        - fig(bytes): the spectrogram encoded in base64
        '''
        self.send(topic=self.TOPIC_SPECTROGRAM, text=json.dumps({"fig": fig}))
        if self.__verbose:
            print("Published spectrogram")

    def send_antenna(self, powers: list[float], received: list[int],
                     selected: list[int]):
        '''
        A convinent function to send antenna data.
        ### Args
        - powers(list[float]): the power of each antenna with a fixed size of 16.
        - received(list[float]): the received power differences with a fixed size of 16.
        - selected(list[int]): the selected antennas
        '''
        self.send(topic=self.TOPIC_ANTENNA,
                  text=json.dumps({
                      "powers":
                      [pwr if pwr is not None else None for pwr in powers],
                      "received":
                      [pd if pd is not None else None for pd in received],
                      "selected":
                      selected
                  }))
        if self.__verbose:
            print(
                f"Published antenna data: powers={powers}, received={received}, selected={selected}"
            )

    def send_pf(self, fig: bytes):
        '''
        A convinent function to send particle filter state.
        '''
        self.send(topic=self.TOPIC_PF, text=json.dumps({"fig": fig}))
        if self.__verbose:
            print("Published PF state")

    def send_message(self, level: MessageLevel, message: str):
        '''
        A convinent function to send messages.
        '''
        text = json.dumps({"level": level, "text": message})
        self.send(topic=self.TOPIC_MESSAGE, text=text)
        if self.__verbose:
            print(f"Published level={level}, text= {text}")

    def info(self, text: str):
        '''
        A convinent function to send info messages.
        '''

        self.send_message(MessageLevel.info, text)

    def debug(self, text: str):
        '''
        A convinent function to send debug messages.
        '''
        self.send_message(MessageLevel.debug, text)

    def warning(self, text: str):
        '''
        A convinent function to send warning messages.
        '''
        self.send_message(MessageLevel.warning, text)

    def error(self, text: str):
        '''
        A convinent function to send error messages.
        '''
        self.send_message(MessageLevel.error, text)


if __name__ == "__main__":
    debugger = MqttDebugger(broker="10.0.4.93", verbose=True)
    debugger.send_antenna(powers=[
        None, -14.1, 10.5, None, None, None, None, None, -12.0, -4.5, None,
        None, None, None, None, None
    ],
                          received=[
                              None, None, 0, 4.3, 3.5, None, None, 1.4, None,
                              None, None, None, None, None, None
                          ],
                          selected=[15])
    import time
    time.sleep(1)
