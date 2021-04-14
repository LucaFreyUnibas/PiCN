import PySimpleGUI as sg
from PiCN.ProgramLibs.Chat import Chatclient

class ChatGUI(object):
    def __init__(self, chatclient: Chatclient, peer: str):
        self.chatclient = chatclient
        print(self.chatclient.get_log())
        layout = [
            [sg.Text('Your chat with ' + peer)],
            [sg.Output(key='ChatLog', size=(30, 10))],
            [sg.InputText(key='ChatInput', size=(25, 4)), sg.Submit(button_text='Send')]
        ]

        window = sg.Window('Chattool', layout)
        while True:
            event, values = window.read(timeout=1000)
            window.Element('ChatLog').Update(self.chatclient.get_log())
            #self.chatclient.send_message('Was geht')
            if event == 'Send':
                    try:
                        if values['ChatInput'] != '':
                            self.chatclient.send_message('Me: ' + values['ChatInput'])
                            window.Element('ChatLog').Update(self.chatclient.get_log())
                            window['ChatInput'].update('')
                    except:
                        print('iamhere2')
            if event == sg.WIN_CLOSED:
                break
        window.close()
