# ChildrenPlusBot

1. Создать файл .env на основе .env.example

```
cp .env.example .env
```

2. Отредактировать .env в соответствие с вашими данными
3. Запустить docker-compose

**Запуск на сервере**

```
docker-compose up -d --build
```

**Тестирование локально**

```
docker-compose up --build
```
*В данном случае контейнеры будут прикреплены к терминалу и будут отображаться их логи. Для их остановки используйте CTRL+C*

4. При редактировании файлов повторите предыдущий пункт