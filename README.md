# Foodgram: Продуктовый помошник

**Foodgram** - это сервис для различный рецептов приготовления пищи. Здесь пользователи могут публиковать свои рецепты и просматривать рецепты других авторов. При публикаци рецепта пользователь выбирает и добавляет в него ингредиенты из предложенного списка, выбирает к какой трапезе (-зам) блюдо более подходит (завтрак/обед/ужин), прикладывает фотографию готового блюда.

Если пользователю нравится чужой рецепт - он может добавить его в избранное: для этого он должен нажать на **"звёздочку"**. После этого этот рецепт будет отображаться на странице **"Избранное"**. 
Если пользователю нравятся рецепты какого-то конкретного автора, то он может подписаться на этого автора: для этого он должен зайти на страницу автора или страницу любого из его рецептов и нажать на кнопку **"Подписаться на автора"**. После этого автор и его рецепты появятся на странице **"Мои подписки"**.
Также пользователь может сформировать список необходимых ему ингредиентов для готовки, иначе говоря - список покупок: для этого он должен нажать на кнопку **"+ Добавить в покупки"** под любым рецептом или рецептами, после чего все они появятся на странице **"Список покупок"**. Там пользователь может нажать на кнопку **"Скачать список"** и получить список необходимых ингредиентов для покупки в формате **".txt"**.

Производить любые операции с рецептами могут только **аутентифицированные пользователи**. Пользователи не прошедшие автторизацию могут только просматривать рецепты.

# Рабочий сайт проекта
https://foodgram-mikhaylets.didns.ru/

# Инструкция по запуску
Для работы проекта необходимо приложение **Docker**.

Репозиторий проекта находится по адресу:
https://github.com/DarkArX89/foodgram-project-react 
Склонируйте его командой:
```
git clone git@github.com:DarkArX89/foodgram-project-react.git
```
В терминале (или командной строке) перейдите в папку с проектом и выполните команду `docker compose up`. 

Проект запущен и доступен по адресу [127.0.0.1:8000](http://127.0.0.1:8000/).

## Примеры запросов к API

### Получение списка всех рецептов:
```
get http://127.0.0.1:8000/api/recipes/
```
### Добавление нового рецепта:
```
post http://127.0.0.1:8000/api/recipes/
```
##### в теле запроса нужно передать:
```
{
  "ingredients": [
    {
      "id": 1,
      "amount": 10
    }
  ],
  "tags": [ 
    1,
    2
  ],
  "image": "<картинка, закодированная в Base64>",
  "name": "Название рецепта",
  "text": "Описание рецепта",
  "cooking_time": 1
}
```
где "ingredients" - список ингредиентов (id ингредиента и его количество), "tags" - список трапез (по id; завтрак/обед/ужин), "cooking_time" - время приготовления.

### Удаление рецепта:
```
delete http://127.0.0.1:8000/api/recipes/{id}/
```

### Получение списка всех ингредиентов:
```
get http://127.0.0.1:8000/api/ingredients/
```

### Получение подписок: 
```
get http://127.0.0.1:8000/api/users/subscriptions/
```

### Подписаться на пользователя
```
post http://127.0.0.1:8000/api/users/{id}/subscribe/
```

## Использованные технологии:
Для разработки проекта использовался язык программирования **python** версии 3.9, а также следующие фреймворки:
 - Django 3.2
 - Django REST framework
 - SImple JWT
 - Djoser

## Автор
**Иван Михайлец**
