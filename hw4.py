# импорт библиотек
import dash

from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import psycopg2
from datetime import date


#подключение к базе данных

conn = psycopg2.connect(user = 'postgres', 
                        database = 'postgres', 
                        host = 'localhost', 
                        port = '5432',
                        password = 'ВВЕДИТЕ ПАРОЛЬ')

# Вспомогательный запрос для получения списка всех существовавших в базе облигаций Альфа-Банка
alpha_isins = pd.read_sql('SELECT DISTINCT isin FROM bond_quotes WHERE issuer = \'Альфа-Банк\'', conn)

# Запуск дашборда
tool = dash.Dash(__name__)

# Сперва создается заголовок и подзаголовок дашборда, а после идет его краткое описание.
tool.layout = html.Div(
        children = [html.H1(children = 'Анализ облигаций Альфа-Банка (by Календа Алексей)'),
                    html.H2(children = 'Анализ объема торгов за определенный период'),
                    html.P(children = 'Описание: дашборд позволяет отобрать по номеру интересующую облигацию Альфа-Банка и посмотреть на объемы торгов по ней за определенный промежуток времени. Его можно указать, заполнив поля даты начала и даты конца.'),
    
# Создается фильтр по облигацям          
           html.Div(
               children = [html.Div(children = 'Выберете облигацию'),
                          dcc.Dropdown(
                                      id = 'isin_filter',
                                      options = [
                                              {'label':isin, 'value':isin}
                                               for isin in alpha_isins['isin']
                                                ],
                                      value = 'RU000A0JWPV3',
                                      clearable = False
                                      )
                          ]
           ),
    
# Создаются фильтры по датам начала и конца рассматриваемого пользователем периода                    
                    html.Div(
               children = [html.Div(children = 'Выберете дату начала'),
                          dcc.DatePickerSingle(
                                        id = "date_start",
                                        month_format = 'MMM Do, YY',
                                        placeholder = 'MMM Do, YY',
                                        date=date.today()
                                         )
                          ]
           ),
    
                    html.Div(
                               children = [html.Div(children = 'Выберете дату конца'),
                                          dcc.DatePickerSingle(
                                                        id = "date_end",
                                                        month_format = 'MMM Do, YY',
                                                        placeholder = 'MMM Do, YY',
                                                        date=date.today()
                                                         )
                                          ]
                    ),
                    
# Пустой базовый график, который будет заполнятся по итогам выполнения функции                    
              dcc.Graph( id = 'Bonds_turnover')         
                   ])

# Параметры функции, которые будут изменяться при изменениях на сервере.
@tool.callback( Output('Bonds_turnover', 'figure'), Input('isin_filter', 'value'),
                                                 Input('date_start', 'date'), 
                                                 Input('date_end', 'date'))
               
def my_fun(isin, date_1, date_2):
    
    # из базы данных запрашивается информация об объеме торгов по облигации Альфа-Банка за определенный промежуток времени
    
    with open('Alpha_bonds.sql', 'r', encoding='utf-8') as f:
            query = (f.read()).format(isin = isin, date_1 = date_1, date_2 = date_2)
    data = pd.read_sql(query, conn)
    
    # Строится столбчатая диаграмма объемов торгов по облигации за выбранный период. Это изображение получается на выходе из функции.
    figure = {"data": 
                    [{"x": data.date_trading,
                      "y": data.turnover,
                      "type": "bar"}], 
             "layout": {"title": "Объем торгов по облигации № {:} с {:} по {:}".format(isin, date_1, date_2)}}
    return figure

 
if __name__ == "__main__":
    tool.run_server()
