from enum import Enum


class Message(Enum):
    WELCOME_IN_GAME = "Привет! Ты находишься в диалоговом квесте. В течении 10 дней твоя задача поговорить " \
                      "с персонажем и выполнить ЗАДАЧУ дня. За один день можно пройти только один диалог. Игра " \
                      "будет спращшивать тебя о таблетках, ведь их приема - залог твоей успешной жизни.В процессе " \
                      "ты узнаешь много полезной информации. В конце тебя ждет СЕРТИФИКАТ об успешном прохождении игры." \
                      " Удачи! "
    ERROR_LACK_OF_CONTENT = "Нет контента, скоро будет"
    ERROR_UNKNOWN_REQUEST = "Мне не чего сказать, скоро будет"


def get_playlist_video():
    return {
        "about": {
            "title": "О фонде",
            "url": ["https://www.youtube.com/watch?v=nbZX40-fo5s&list=PLHmmAVjC0aR1_9lKX_mw2giJsiDmtAhgi&index=1",
                    "https://www.youtube.com/watch?v=hgogVgapFnc&list=PLHmmAVjC0aR1_9lKX_mw2giJsiDmtAhgi&index=5"
                    ]
        },
        "support_family": {
            "title": "Поддержка семей",
            "url": ["https://www.youtube.com/watch?v=Tioc2WJWGeY&list=PLHmmAVjC0aR0RTBzb9p433PmHHJRxTk9P",
                    "https://www.youtube.com/watch?v=zLEdt21TkkA&list=PLHmmAVjC0aR0RTBzb9p433PmHHJRxTk9P&index=2"
                    ]
        },
        "experts": {
            "title": "Специалистам, помогающим с ВИЧ",
            "url": ["https://www.youtube.com/watch?v=9qTSd9NsyOs&list=PLHmmAVjC0aR1dYDznI9u1rCp-3oecY9Vp",
                    "https://www.youtube.com/watch?v=1EEmx_7xa9Q&list=PLHmmAVjC0aR1dYDznI9u1rCp-3oecY9Vp&index=2"
                    ]
        }
    }


def get_game():
    return {
        "start": {
            "question": "Вы сегодня уже выпили терапию?",
            "answer1": "Да, конечно",
            "answer2": "Почему вас это интересует? Это мое дело!"
        },
        "Да, конечно": {
            "question": "Это здорово! Отличного настроения вам!",
            "answer1": "Спасибо!",
            "answer2": ""
        },
        "Почему вас это интересует? Это мое дело!": {
            "question": "Не забывайте о своевременном приеме лекарств",
            "answer1": "Хорошо",
            "answer2": ""
        },
        "Хорошо": {
            "question": "",
            "answer1": "Завершить игру",
            "answer2": ""
        }
        ,
        "Спасибо!": {
            "question": "",
            "answer1": "Завершить игру",
            "answer2": ""
        }
    }
