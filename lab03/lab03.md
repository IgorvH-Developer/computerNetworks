# Практика 3. Прикладной уровень

## Программирование сокетов. Веб-сервер

### А. Однопоточный веб-сервер (3 балла)
Вам необходимо разработать простой веб-сервер, который будет возвращать содержимое
локальных файлов по их имени. В этом задании сервер умеет обрабатывать только один запрос и
работает в однопоточном режиме. Язык программирования вы можете выбрать любой.
Требования:
- веб-сервер создает сокет соединения при контакте с клиентом (браузером) получает HTTP-запрос из этого соединения
- анализирует запрос, чтобы определить конкретный запрашиваемый файл
- находит запрошенный файл в своей локальной файловой системе
- создает ответное HTTP-сообщение, состоящее из содержимого запрошенного файла и предшествующих ему строк заголовков
- отправляет ответ через TCP-соединение обратно клиенту
- если браузер запрашивает файл, которого нет на веб-сервере, то сервер должен вернуть сообщение об ошибке «404 Not Found»

Ваша задача – разработать и запустить свой локальный веб-сервер, а затем проверить его
работу при помощи отправки запросов через браузер. Продемонстрируйте работу сервера, приложив скрины.

Скорее всего порт 80 у вас уже занят, поэтому вам необходимо использовать другой порт для
работы вашей программы.

Формат команды для запуска сервера:
```
<server.exe> server_port
```

#### Демонстрация работы

1) Создаём файл

<img alt="images/img.png" height="300" src="images/img.png" width="490"/>

2) Запускаем сервер

![images/img_1.png](images/img_1.png)

3) Отправляем запрос с существующим файлом

<img alt="images/img_2.png" height="300" src="images/img_2.png" width="410"/>

4) Отправляем запрос с несуществующим файлом

<img alt="images/img_3.png" height="300" src="images/img_3.png" width="380"/>

### Б. Многопоточный веб-сервер (2 балла)
Реализуйте многопоточный сервер, который мог бы обслуживать несколько запросов
одновременно. Сначала создайте основной поток (процесс), в котором ваш модифицированный
сервер ожидает клиентов на определенном фиксированном порту. При получении запроса на
TCP-соединение от клиента он будет устанавливать это соединение через другой порт и
обслуживать запрос клиента в отдельном потоке. Таким образом, для каждой пары запрос-ответ
будет создаваться отдельное TCP-соединение в отдельном потоке.

#### Демонстрация работы

1) Запустили сервер на порту 8000

![images/img_6.png](images/img_6.png)

2) Отправляем запрос первый раз

![images/img_7.png](images/img_7.png)

Видим, что порт клиента отличается от порта сервера
![images/img_8.png](images/img_8.png)

3) Отправляем запрос второй раз

![images/img_9.png](images/img_9.png)

Видим, что порт клиента снова отличается
![images/img_10.png](images/img_10.png)

### В. Клиент (2 балла)
Вместо использования браузера напишите собственный HTTP-клиент для тестирования вашего
веб-сервера. Ваш клиент будет поддерживать работу с командной строкой, подключаться к
серверу с помощью TCP-соединения, отправлять ему HTTP-запрос с помощью метода GET и
отображать ответ сервера в качестве результата. Клиент должен будет в качестве входных
параметров принимать аргументы командной строки, определяющие IP-адрес или имя сервера,
порт сервера и имя файла на сервере. Продемонстрируйте работу клиента, приложив скрины. 

Формат команды для запуска клиента:
```
<client.exe> server_host server_port filename
```

#### Демонстрация работы

1) Запуск сервера

![images/img_11.png](images/img_11.png)

2) Запуск клиента, отправляющего HTTP GET запрос на сервер

![images/img_12.png](images/img_12.png)

3) Запуск клиента с неправильным портом сервера

![images/img_13.png](images/img_13.png)

### Г. Ограничение потоков сервера (3 балла)
Пусть ресурсы вашего сервера ограничены и вы хотите контролировать максимальное количество
потоков, с которыми может работать ваш многопоточный сервер одновременно. При запуске
сервер получает целочисленное значение `concurrency_level` из командной строки. Если сервер 
получает запрос от клиента, и при этом уже запущено максимальное количество потоков, то 
запрос от клиента блокируется (встает в очередь) и дожидается, пока не закончит работу 
один из запущенных потоков. После этого сервер может запустить новый поток для обработки 
запроса от клиента.

Формат команды для запуска сервера:
```
<server.exe> server_port concurrency_level
```

## Задачи

### Задача 1 (2 балла)
Голосовые сообщения отправляются от хоста А к хосту Б в сети с коммутацией пакетов в режиме
реального времени. Хост А преобразует на лету аналоговый голосовой сигнал в цифровой поток
битов, имеющий скорость $128$ Кбит/с, и разбивает его на $56$-байтные пакеты. Хосты А и Б
соединены одной линией связи, в которой скорость передачи данных равна $1$ Мбит/с, а задержка
распространения составляет $5$ мс. Как только хост А собирает пакет, он посылает его на хост Б,
который, в свою очередь, при получении всего пакета преобразует биты в аналоговый сигнал.
Сколько времени проходит с момента создания бита (из исходного аналогового сигнала на хосте
A) до момента его декодирования (превращения в часть аналогового сигнала на хосте Б)?

#### Решение

1) Создание пакета

$T_{преобразования} = \dfrac{пакет}{скорость \space преобразования} = \dfrac{56 * 8}{128 * 2^{10}} = 0.0034$ сек

2) Передача пакета

$T_{передачи} = \dfrac{пакет}{скорость \space передачи} = \dfrac{56 * 8}{1 * 2^{20}} = 0.00043$ сек

3) Общее время

$T_{общее} = T_{преобразования} + T_{передачи} + T_{задержки} = 0.0034 + 0.00043 + 0.005 = 0.00883$ сек

Ответ: примерно $0.009$ сек

### Задача 2 (2 балла)
Рассмотрим буфер маршрутизатора, где пакеты хранятся перед передачей их в исходящую линию
связи. В этой задаче вы будете использовать широко известную из теории массового
обслуживания (или теории очередей) формулу Литтла. Пусть $N$ равно среднему числу пакетов в
буфере плюс пакет, который передается в данный момент. Обозначим через $a$ скорость
поступления пакетов в буфер, а через $d$ – среднюю общую задержку (т.е. сумму задержек
ожидания и передачи), испытываемую пакетом. Согласно формуле Литтла $N = a \cdot d$.
Предположим, что в буфере содержится в среднем $10$ пакетов, а средняя задержка ожидания для
пакета равна $10$ мс. Скорость передачи по линии связи составляет $100$ пакетов в секунду.
Используя формулу Литтла, определите среднюю скорость поступления пакета в очередь,
предполагая, что потери пакетов отсутствуют.

#### Решение

Дано:

$N = 10$

$t_{ожидания} = 0.01$ сек

$v_{передачи} = 100 \space пакетов/сек$ Следовательно скорость передачи одного пакета будет $0.01$ сек  

Решение:

$d = t_{ожидания} + t_{передачи} = 0.01 + 0.01 = 0.02$ сек

$a = \dfrac{N}{d} = \dfrac{10}{0.02} = 500 \space пакетов/сек$

### Задача 3 (2 балла)
Рассмотрим рисунок.

<img src="images/task3.png" width=500 />

Предположим, нам известно, что на маршруте от сервера до клиента узким местом
является первая линия связи, скорость передачи данных по которой равна $R_S$ бит/с.
Допустим, что мы отправляем два пакета друг за другом от сервера клиенту, и другой
трафик на маршруте отсутствует. Размер каждого пакета составляет $L$ бит, а скорость
распространения сигнала по обеим линиям равна $d_{\text{распространения}}$.
1. Какова временная разница прибытия пакетов к месту назначения? То есть, сколько
времени пройдет от момента получения клиентом последнего бита первого пакета до
момента получения последнего бита второго пакета?
2. Теперь предположим, что узким местом является вторая линия связи (то есть $R_C < R_S$).
Может ли второй пакет находиться во входном буфере, ожидая передачи во вторую
линию? Почему? Если предположить, что сервер отправляет второй пакет, спустя $T$ секунд
после отправки первого, то каково должно быть минимальное значение $T$, чтобы очередь
во вторую линию связи была нулевая? Обоснуйте ответ.

#### Решение

1. Первый пункт

Задержка будет складываться из времени передачи второго пакета и задержки распространения

Время передачи пакета $T_1 = \dfrac{L}{R_s}$

$T{разница} = T_1 + d_{распространения} = \dfrac{L}{R_s} + d_{распространения}$

2. Второй пункт

Так как $R_C < R_S$, то это значит, что данные на вторую линию поступают быстрее, чем она их отдаёт.

Первая линия - это поток воды, льющийся в ведро, а второя линия - это дырка на дне ведра. 
Вода не может выливаться через дырку одновременно с потоком воды из крана, поэтому она копиться.

Чтобы избежать очереди, нужно убедиться что второй пакет доходит до второй линии в тот момент,
когда она завершила отправку первого. То есть:

$T_{min} = \dfrac{L}{R_c} - d_{распространения}$

Так как нам нужно дождаться, пока вторая линиия освободиться, и только потом начинать передавать второй пакет,
поэтому считаем сколько времени займёт передача первого пакета по второй линии. А также, из полученного
времени вычитаем $d_{распространения}$, так как в это время второй пакет будет только в пути, и 
вторая линия может всё ещё быть занята передачей первого пакета.


### Задача 4 (4 балла)

<img src="images/task4.png" width=400 />

На рисунке показана сеть организации, подключенная к Интернету:
Предположим, что средний размер объекта равен $850000$ бит, а средняя скорость
запросов от браузеров этой организации к веб-серверам составляет $16$ запросов в секунду.
Предположим также, что количество времени, прошедшее с момента, когда внешний
маршрутизатор организации пересылает запрос HTTP, до момента, пока он не получит
ответ, равно в среднем три секунды. Будем считать, что общее среднее время ответа
равно сумме средней задержки доступа (то есть, задержки от маршрутизатора в
Интернете до маршрутизатора организации) и средней задержки в Интернете. Для
средней задержки доступа используем формулу $\dfrac{\Delta}{1 - \Delta \cdot B}$, 
где $\Delta$ – это среднее время, необходимое для отправки объекта по каналу связи, 
а B – частота поступления объектов в линию связи.
1. Найдите $\Delta$ (это среднее время, необходимое для отправки объекта по каналу связи).
2. Найдите общее среднее время ответа.
3. Предположим, что в локальной сети организации присутствует кэширующий
сервер. Пусть коэффициент непопадания в кэш равен $0.4$. Найдите общее время ответа.

#### Решение

1) Найдите $\Delta$

Скорость канала доступа = $15 * 10^6$ бит/с. Скорость ЛВС = $100 * 10^6$ бит/с. Средняя длина объекта = 850000 бит.
Канала доступа - это узкое место, следовательно, время передачи объекта $\Delta = \dfrac{850000}{15 * 10^6} = 0,057$ сек.

2) Найдите общее среднее время ответа.

Среднее время ответа $T_{общ} = \dfrac{\Delta}{1 - \Delta \cdot B} + средняя \space задержка \space в \space интернете =
\dfrac{0,057}{1 - 0,057 \cdot 16} + 3 = 0,648 + 3 = 3,648$ сек

3) общее время ответа с кэшем

$T_{кэш}$ - время получения объекта из кэша

Общее время ответа с кэшем:

$T = T_{общ} * 0,4 + (T_{общ} + T_{кэш}) * 0,6$

