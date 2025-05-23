# Практика 2. Rest Service

## Программирование. Rest Service. Часть I

### Задание А (3 балла)
Создайте простой REST сервис, в котором используются HTTP операции GET, POST, PUT и DELETE.
Предположим, что это сервис для будущего интернет-магазина, который пока что умеет 
работать только со списком продуктов. У каждого продукта есть поля: `id` (уникальный идентификатор),
`name` и `description`. 

Таким образом, json-схема продукта (обозначим её `<product-json>`):

```json
{
  "id": 0,
  "name": "string",
  "description": "string"
}
```

Данные продукта от клиента к серверу должны слаться в теле запроса в виде json-а, **не** в параметрах запроса.

Ваш сервис должен поддерживать следующие операции:
1. Добавить новый продукт. При этом его `id` должен сгенерироваться автоматически
   - `POST /product`
   - Схема запроса:
     ```json
     {
       "name": "string",
       "description": "string"
     }
     ```
   - Схема ответа: `<product-json>` (созданный продукт)
2. Получить продукт по его id
   - `GET /product/{product_id}`
   - Схема ответа: `<product-json>`
3. Обновить существующий продукт (обновляются только те поля продукта, которые были переданы в теле запроса)
   - `PUT /product/{product_id}`
   - Схема запроса: `<product-json>` (некоторые поля могут быть опущены)
   - Схема ответа: `<product-json>` (обновлённый продукт)
4. Удалить продукт по его id
   - `DELETE /product/{product_id}`
   - Схема ответа: `<product-json>` (удалённый продукт)
5. Получить список всех продуктов 
   - `GET /products`  
   - Схема ответа:
     ```
     [ 
       <product-json-1>,
       <product-json-2>, 
       ... 
     ]
     ```

Предусмотрите возвращение ошибок (например, если запрашиваемого продукта не существует).

Вы можете положить код сервиса в отдельную директорию рядом с этим документом.

### Задание Б (3 балла)
Продемонстрируйте работоспособность сервиса с помощью программы Postman
(https://www.postman.com/downloads) и приложите соответствующие скрины, на которых указаны
запросы и ответы со стороны сервиса для **всех** его операций.

#### Демонстрация работы

1) Создание двух продуктов

   <img alt="img.png" height="400" src="images/img.png" width="260"/>

   <img alt="img_1.png" height="400" src="images/img_1.png" width="260"/>

2) Получение информации по продуктам

    <img alt="img_2.png" height="400" src="images/img_2.png" width="260"/>

   <img alt="img_3.png" height="400" src="images/img_3.png" width="260"/>

3) Обновление поля продукта

   <img alt="img_4.png" height="400" src="images/img_4.png" width="260"/>

   <img alt="img_5.png" height="400" src="images/img_5.png" width="260"/>

4) Удаление продукта

   <img alt="img_6.png" height="400" src="images/img_6.png" width="260"/>

5) Получение списка продуктов

   <img alt="img_7.png" height="400" src="images/img_7.png" width="260"/>
    

### Задание В (4 балла)
Пусть ваш продукт также имеет иконку (небольшую картинку). Формат иконки (картинки) может
быть любым на ваш выбор. Для простоты будем считать, что у каждого продукта картинка одна.

Добавьте две новые операции:
1. Загрузить иконку:
   - `POST product/{product_id}/image`
   - Запрос содержит бинарный файл — изображение  
     <img src="images/post-image.png" width=500 />
2. Получить иконку:
   - `GET product/{product_id}/image`
   - В ответе передаётся только сама иконка  
     <img src="images/get-image.png" width=500 />

Измените операции в Задании А так, чтобы теперь схема продукта содержала сведения о загруженной иконке, например, имя файла или путь:
```json
"icon": "string"
```

#### Демонстрация работы

1) Загрузка иконки

<img alt="images/img_10.png" height="400" src="images/img_10.png" width="260"/>

<img alt="images/img_12.png" height="400" src="images/img_12.png" width="330"/>


2) Получение иконки

![images/img_11.png](images/img_11.png)

---

_(*) В последующих домашних заданиях вам будет предложено расширить функционал данного сервиса._

## Задачи

### Задача 1 (2 балла)
Общая (сквозная) задержка прохождения для одного пакета от источника к приемнику по пути,
состоящему из $N$ соединений, имеющих каждый скорость $R$ (то есть между источником и
приемником $N - 1$ маршрутизатор), равна $d_{\text{сквозная}} = N \dfrac{L}{R}$
Обобщите данную формулу для случая пересылки количества пакетов, равного $P$.

#### Решение

Если передача следующего пакета на ближайшем к источнике маршрутизатору начинается сразу,
после того как он обработал предыдущий пакет, то задержка передачи P паектов будет равна: 

$d = (N + P — 1) * \dfrac{L}{R}$

Это можно описать как цепочку рабочих предающих друг другу кирпичи. 
Чтобы передать 10 кирпичей, первому рабочему нужно сначала передать своему соседу по
цепочке 9 кирпичей (что займёт 9 * время передачи одного кирпича рабочим, то есть 
$9 * \dfrac{L}{R}$), а потом начнётся передача последнего кирпича по всей цепочке, 
а эту задержку мы уже знаем, она равна $N * \dfrac{L}{R}$

### Задача 2 (2 балла)
Допустим, мы хотим коммутацией пакетов отправить файл с хоста A на хост Б. Между хостами установлены три
последовательных канала соединения со следующими скоростями передачи данных:
$R_1 = 200$ Кбит/с, $R_2 = 3$ Мбит/с и $R_3 = 2$ Мбит/с.
Сколько времени приблизительно займет передача на хост Б файла размером $5$ мегабайт?
Как это время зависит от размера пакета?

#### Решение

Так как соединение последовательное, то скорость передачи пакета равняется скорости передачи данных самого медленного соединения, у нас это соединение R_1.
Поэтому:
$t = \dfrac{packet \space size}{R_1} = \dfrac{5 * 8 * 2^{10}}{200} = 204,8 \space сек$

Время передачи пакета прямо пропорционально его размеру.

### Задача 3 (2 балла)
Предположим, что пользователи делят канал с пропускной способностью $2$ Мбит/с. Каждому
пользователю для передачи данных необходима скорость $100$ Кбит/с, но передает он данные
только в течение $20$ процентов времени использования канала. Предположим, что в сети всего $60$
пользователей. А также предполагается, что используется сеть с коммутацией пакетов. Найдите
вероятность одновременной передачи данных $12$ или более пользователями.

#### Решение

Вероятность того, что пользователь передаёт данные $p=0.2$. А вероятность того, что $k$ 
пользователей передаёт данные можно описать биномиальным распределением:
$P(X=k) = C^k_n p^k (1-p)^{n-k}$

А чтобы получить вероятность, что 12 или более пользователей передают данные, нужно вычислить P(X>=12).
Вычислить это можно по следующей формуле:

![images/img_8.png](images/img_8.png)

и ответом будет:

![images/img_9.png](images/img_9.png)


### Задача 4 (2 балла)
Пусть файл размером $X$ бит отправляется с хоста А на хост Б, между которыми три линии связи и
два коммутатора. Хост А разбивает файл на сегменты по $S$ бит каждый и добавляет к ним
заголовки размером $80$ бит, формируя тем самым пакеты длиной $L = 80 + S$ бит. Скорость
передачи данных по каждой линии составляет $R$ бит/с. Загрузка линий мала, и очередей пакетов
нет. При каком значении $S$ задержка передачи файла между хостами А и Б будет минимальной?
Задержкой распространения сигнала пренебречь.

#### Решение

Время передачи одного пакета: $T = \dfrac{L}{R}$

Оптимальнее всего будет распределить пакеты по всем линия равномерно, то 
есть нужно разбить файл на количество пакетов кратное 3. А также, нужно чтобы 
этих троек пакетов было минимально количество, чтобы передавать как можно меньше 
заголовков пакетов.

Получаем следующее:
$N = [\dfrac{X}{S}]$ (округление вверх)

Самым оптимальным вариантом будет $N=3$, следовательно: $S = [\dfrac{X}{3}]$

### Задание 5 (2 балла)
Рассмотрим задержку ожидания в буфере маршрутизатора. Обозначим через $I$ интенсивность
трафика, то есть $I = \dfrac{L a}{R}$.
Предположим, что для $I < 1$ задержка ожидания вычисляется как $\dfrac{I \cdot L}{R (1 – I)}$. 
1. Напишите формулу для общей задержки, то есть суммы задержек ожидания и передачи.
2. Опишите зависимость величины общей задержки от значения $\dfrac{L}{R}$.

#### Решение

Задержка передачи определяется как:

$D_{пер} = \dfrac{L}{R}$

Задержка ожидания:

$D_{ож} = \dfrac{I \cdot L}{R (1 – I)}$

Общая задержка:

$D_{общ} = D_{пер} + D_{ож} = \dfrac{I \cdot L}{R (1 – I)} + \dfrac{L}{R} = \dfrac{L}{R(1-I)}$

Общая задержка прямо пропорциональна значению $\dfrac{L}{R}$
 
