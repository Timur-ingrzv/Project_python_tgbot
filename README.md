# Описание проекта
Данный проект направлен на создание Telegram-бота для взаимодействия с учениками, который облегчит процесс уведомления о занятиях, предоставит удобный доступ к конспектам, соберёт и визуализирует статистику посещаемости и успеваемости, а также предложит возможность оставлять отзывы после каждого занятия.


## Содержание
- [Цели проекта](#цели-проекта)

- [Функционал](#функционал)

- [Используемые технологии](#используемые-технологии)


## Цели проекта
- Уведомление учеников о предстоящих занятиях.

- Предоставление быстрых доступов к конспектам по выбранным темам.

- Сбор и визуализация статистики занятий, успеваемости.

- Возможность оставить отзыв об уроке.

## Функционал
Телеграмм-бот предоставляет функционал для учеников и репетиторов

- **Функционал ученика**
  1. Просмотр запланированных уроков\
  Возможность увидеть дату и тему занятия.
  2. Просмотр назначенных домашних заданий до делайна\
  Возможность получить ссылку на задание и видеть дату сдачи работы.

  3. Отправка домашнего задания
  Возможность с помощью тг-бота отправить файл на яндекс диск

  4. Составление отзыва о занятии

  5. Выход из профиля


- **Функционал репетитора**
  1. Добавление нового ученика

  2. Назначение домашнего задания

  3. Управление расписанием

  4. Просмотр статистики проведенных занятий за период

  5. Просмотр статистики успеваемости ученика
  
## Используемые технологии

- **Telegram-бот** - интерфейс для пользователя


- **Yandex disk** - хранение конспекта, выданных домашних заданий и выполненных учеником домашних заданий


- **Реляционная база данных** - хранение информации о пользователе, домашних заданиях и занятий**
 
  Структура базы данных:
    !['df'](/db.png)
   