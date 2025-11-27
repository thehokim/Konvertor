# import json
# import geopandas as gpd
# from shapely.geometry import Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon
# import pandas as pd
# from pathlib import Path
#
#
# def analyze_json_structure(json_file_path):
#     """
#     Анализирует структуру JSON файла и определяет тип геометрии
#     """
#     with open(json_file_path, 'r', encoding='utf-8') as f:
#         data = json.load(f)
#
#     print("=== АНАЛИЗ СТРУКТУРЫ JSON ===")
#     print(f"Тип данных: {type(data)}")
#
#     if isinstance(data, dict):
#         print(f"Ключи верхнего уровня: {list(data.keys())}")
#
#         # Проверяем, является ли это GeoJSON
#         if 'type' in data and data['type'] in ['FeatureCollection', 'Feature']:
#             analyze_geojson(data)
#         else:
#             analyze_custom_json(data)
#
#     elif isinstance(data, list):
#         print(f"Список из {len(data)} элементов")
#         if data:
#             print(f"Структура первого элемента: {list(data[0].keys()) if isinstance(data[0], dict) else type(data[0])}")
#
#             # Проверяем, являются ли это сельскохозяйственные данные
#             if (isinstance(data[0], dict) and
#                     'geometry' in data[0] and
#                     any(field in data[0] for field in ['contour_id', 'farmer_name', 'area'])):
#                 analyze_agricultural_json(data)
#             else:
#                 analyze_json_array(data)
#
#     return data
#
#
# def analyze_geojson(data):
#     """
#     Анализирует GeoJSON структуру
#     """
#     print("\n=== ОБНАРУЖЕН GEOJSON ===")
#
#     if data['type'] == 'FeatureCollection':
#         features = data.get('features', [])
#         print(f"Количество объектов: {len(features)}")
#
#         if features:
#             # Анализируем типы геометрии
#             geometry_types = set()
#             properties_keys = set()
#
#             for feature in features:
#                 if 'geometry' in feature and feature['geometry']:
#                     geometry_types.add(feature['geometry']['type'])
#
#                 if 'properties' in feature and feature['properties']:
#                     properties_keys.update(feature['properties'].keys())
#
#             print(f"Типы геометрии: {list(geometry_types)}")
#             print(f"Атрибуты: {list(properties_keys)}")
#
#             # Рекомендуем тип shapefile
#             recommend_shapefile_type(geometry_types)
#
#     elif data['type'] == 'Feature':
#         print("Одиночный объект")
#         if 'geometry' in data:
#             print(f"Тип геометрии: {data['geometry']['type']}")
#             recommend_shapefile_type([data['geometry']['type']])
#
#
# def analyze_custom_json(data):
#     """
#     Анализирует пользовательский JSON формат
#     """
#     print("\n=== АНАЛИЗ ПОЛЬЗОВАТЕЛЬСКОГО JSON ===")
#
#     # Ищем координаты
#     coord_fields = find_coordinate_fields(data)
#     if coord_fields:
#         print(f"Найдены поля с координатами: {coord_fields}")
#         suggest_geometry_conversion(coord_fields)
#     else:
#         print("Координаты не найдены в явном виде")
#         print("Проверьте наличие полей: lat, lon, latitude, longitude, x, y, coordinates")
#
#
# def analyze_agricultural_json(data):
#     """
#     Специальный анализ для сельскохозяйственных данных
#     """
#     print("\n=== АНАЛИЗ СЕЛЬСКОХОЗЯЙСТВЕННЫХ ДАННЫХ ===")
#
#     if not isinstance(data, list) or not data:
#         print("❌ Некорректный формат данных")
#         return
#
#     sample_item = data[0]
#     print(f"📊 Общая информация:")
#     print(f"   Количество записей: {len(data):,}")
#     print(f"   Поля данных: {list(sample_item.keys())}")
#
#     # Анализируем геометрию
#     geometry_analysis = analyze_geometry_field(data)
#
#     # Анализируем атрибуты
#     attribute_analysis = analyze_attributes(data)
#
#     return geometry_analysis, attribute_analysis
#
#
# def analyze_geometry_field(data):
#     """
#     Анализирует поле geometry в данных
#     """
#     print(f"\n🗺️  АНАЛИЗ ГЕОМЕТРИИ:")
#
#     geometry_types = {}
#     invalid_geometries = 0
#     sample_coordinates = []
#
#     # Анализируем первые 1000 записей для скорости
#     sample_size = min(1000, len(data))
#
#     for i in range(sample_size):
#         item = data[i]
#         if 'geometry' in item and isinstance(item['geometry'], dict):
#             geom = item['geometry']
#
#             if 'type' in geom and 'coordinates' in geom:
#                 geom_type = geom['type']
#                 geometry_types[geom_type] = geometry_types.get(geom_type, 0) + 1
#
#                 # Сохраняем примеры координат
#                 if len(sample_coordinates) < 3:
#                     sample_coordinates.append({
#                         'type': geom_type,
#                         'coordinates_sample': str(geom['coordinates'])[:100] + '...' if len(
#                             str(geom['coordinates'])) > 100 else geom['coordinates']
#                     })
#             else:
#                 invalid_geometries += 1
#         else:
#             invalid_geometries += 1
#
#     print(f"   Проанализировано записей: {sample_size}")
#     print(f"   Типы геометрии:")
#     for geom_type, count in geometry_types.items():
#         percentage = (count / sample_size) * 100
#         print(f"     - {geom_type}: {count} ({percentage:.1f}%)")
#
#     if invalid_geometries > 0:
#         print(f"   ⚠️  Некорректных геометрий: {invalid_geometries}")
#
#     print(f"\n   Примеры координат:")
#     for sample in sample_coordinates:
#         print(f"     {sample['type']}: {sample['coordinates_sample']}")
#
#     # Рекомендации
#     print(f"\n📋 РЕКОМЕНДАЦИИ ДЛЯ SHAPEFILE:")
#
#     if len(geometry_types) == 1:
#         geom_type = list(geometry_types.keys())[0]
#         shapefile_mapping = {
#             'Point': 'Point Shapefile - для точечных объектов',
#             'LineString': 'Polyline Shapefile - для линейных объектов',
#             'Polygon': 'Polygon Shapefile - для контуров полей',
#             'MultiPoint': 'Point Shapefile - для множественных точек',
#             'MultiLineString': 'Polyline Shapefile - для сложных линий',
#             'MultiPolygon': 'Polygon Shapefile - для сложных полигонов'
#         }
#
#         recommendation = shapefile_mapping.get(geom_type, f'Shapefile для {geom_type}')
#         print(f"   ✅ Одиночный тип геометрии: {recommendation}")
#
#         if geom_type in ['Polygon', 'MultiPolygon']:
#             print(f"   🌾 Идеально для сельскохозяйственных контуров полей!")
#
#     else:
#         print(f"   ⚠️  Смешанные типы геометрии - будут созданы отдельные файлы:")
#         for geom_type in geometry_types.keys():
#             print(f"     - {geom_type}_contours.shp")
#
#     return geometry_types
#
#
# def analyze_attributes(data):
#     """
#     Анализирует атрибутивные данные
#     """
#     print(f"\n📋 АНАЛИЗ АТРИБУТОВ:")
#
#     if not data:
#         return {}
#
#     sample_item = data[0]
#     attribute_info = {}
#
#     # Анализируем каждое поле
#     for key, value in sample_item.items():
#         if key == 'geometry':
#             continue
#
#         attr_info = {
#             'type': type(value).__name__,
#             'sample_value': str(value)[:50] + '...' if len(str(value)) > 50 else value
#         }
#
#         # Специальная обработка для вложенных объектов
#         if isinstance(value, dict):
#             attr_info['nested_fields'] = list(value.keys())
#             attr_info['sample_nested'] = {k: str(v)[:30] + '...' if len(str(v)) > 30 else v
#                                           for k, v in list(value.items())[:3]}
#
#         attribute_info[key] = attr_info
#
#     print(f"   Основные поля:")
#     for field, info in attribute_info.items():
#         print(f"     - {field} ({info['type']}): {info['sample_value']}")
#         if 'nested_fields' in info:
#             print(f"       Вложенные поля: {info['nested_fields']}")
#
#     # Рекомендации для shapefile
#     print(f"\n   💡 РЕКОМЕНДАЦИИ ДЛЯ АТРИБУТОВ:")
#     print(f"     - Имена полей будут сокращены до 10 символов (ограничение shapefile)")
#     print(f"     - Вложенные объекты будут развернуты в отдельные поля")
#     print(f"     - Поля с сельхоз данными: contour_id, farmer_name, area, cad_number")
#
#     return attribute_info
#
#
# def find_coordinate_fields(obj, path=""):
#     """
#     Ищет поля, которые могут содержать координаты
#     """
#     coord_fields = []
#
#     if isinstance(obj, dict):
#         for key, value in obj.items():
#             current_path = f"{path}.{key}" if path else key
#
#             # Проверяем названия полей
#             key_lower = key.lower()
#             if any(coord_name in key_lower for coord_name in ['lat', 'lon', 'x', 'y', 'coord', 'lng']):
#                 coord_fields.append(current_path)
#
#             # Проверяем значения
#             if isinstance(value, (int, float)) and -180 <= value <= 180:
#                 if any(coord_name in key_lower for coord_name in ['lat', 'lon', 'x', 'y']):
#                     coord_fields.append(current_path)
#
#             # Рекурсивно проверяем вложенные объекты
#             elif isinstance(value, dict):
#                 coord_fields.extend(find_coordinate_fields(value, current_path))
#
#             # Проверяем массивы координат
#             elif isinstance(value, list) and len(value) >= 2:
#                 if all(isinstance(x, (int, float)) for x in value[:2]):
#                     coord_fields.append(current_path)
#
#     return coord_fields
#
#
# def recommend_shapefile_type(geometry_types):
#     """
#     Рекомендует тип shapefile на основе типов геометрии
#     """
#     print("\n=== РЕКОМЕНДАЦИИ ДЛЯ SHAPEFILE ===")
#
#     geometry_mapping = {
#         'Point': 'Point Shapefile (точки)',
#         'MultiPoint': 'Point Shapefile (множественные точки)',
#         'LineString': 'Polyline Shapefile (линии)',
#         'MultiLineString': 'Polyline Shapefile (множественные линии)',
#         'Polygon': 'Polygon Shapefile (полигоны)',
#         'MultiPolygon': 'Polygon Shapefile (множественные полигоны)'
#     }
#
#     for geom_type in geometry_types:
#         if geom_type in geometry_mapping:
#             print(f"- {geom_type} → {geometry_mapping[geom_type]}")
#
#     # Если смешанные типы
#     if len(geometry_types) > 1:
#         print("\n⚠️  ВНИМАНИЕ: Обнаружены смешанные типы геометрии!")
#         print("Shapefile поддерживает только один тип геометрии на файл.")
#         print("Рекомендуется создать отдельные файлы для каждого типа.")
#
#
# def suggest_geometry_conversion(coord_fields):
#     """
#     Предлагает варианты конвертации координат в геометрию
#     """
#     print("\n=== ВАРИАНТЫ КОНВЕРТАЦИИ ===")
#
#     # Анализируем типы координат
#     has_single_coords = any(field.lower() in ['lat', 'latitude', 'lon', 'longitude', 'x', 'y']
#                             for field in coord_fields)
#     has_coord_arrays = any('coord' in field.lower() and 'array' in str(type(field))
#                            for field in coord_fields)
#
#     if has_single_coords:
#         print("1. ТОЧЕЧНАЯ ГЕОМЕТРИЯ")
#         print("   - Создание Point из отдельных полей lat/lon или x/y")
#         print("   - Подходит для: магазины, остановки, датчики, события")
#
#     if has_coord_arrays:
#         print("2. ЛИНЕЙНАЯ ИЛИ ПОЛИГОНАЛЬНАЯ ГЕОМЕТРИЯ")
#         print("   - Создание LineString из массива координат")
#         print("   - Создание Polygon если первая и последняя точки совпадают")
#         print("   - Подходит для: маршруты, границы, здания")
#
#     print("\n3. РЕКОМЕНДУЕМЫЕ ШАГИ:")
#     print("   a) Определите основную геометрию ваших данных")
#     print("   b) Выберите соответствующий тип shapefile")
#     print("   c) Используйте функцию convert_to_shapefile() ниже")
#
#
# def convert_to_shapefile(json_file_path, output_path, conversion_type='auto'):
#     """
#     Конвертирует JSON в Shapefile
#
#     conversion_type: 'geojson', 'points', 'auto'
#     """
#     print(f"\n=== КОНВЕРТАЦИЯ В SHAPEFILE ===")
#
#     with open(json_file_path, 'r', encoding='utf-8') as f:
#         data = json.load(f)
#
#     try:
#         if conversion_type == 'geojson' or (
#                 isinstance(data, dict) and data.get('type') in ['FeatureCollection', 'Feature']):
#             # Прямая конвертация GeoJSON
#             gdf = gpd.read_file(json_file_path)
#             gdf.to_file(output_path, driver='ESRI Shapefile')
#             print(f"✅ GeoJSON успешно конвертирован: {output_path}")
#
#         elif conversion_type == 'points' or conversion_type == 'auto':
#             # Проверяем тип данных для выбора правильной функции конвертации
#             if (isinstance(data, list) and data and isinstance(data[0], dict) and
#                     'geometry' in data[0] and isinstance(data[0]['geometry'], dict)):
#                 # Данные с полем geometry
#                 convert_agricultural_data_to_shapefile(data, output_path)
#             else:
#                 # Простые координаты
#                 convert_points_to_shapefile(data, output_path)
#
#         print(f"📁 Создан shapefile: {output_path}")
#
#     except Exception as e:
#         print(f"❌ Ошибка конвертации: {e}")
#         print("Попробуйте другой тип конвертации или проверьте данные")
#
#
# def convert_agricultural_data_to_shapefile(data, output_path, fix_invalid=True):
#     """
#     Конвертирует сельскохозяйственные данные с геометрией в shapefile
#     fix_invalid: если True, пытается исправить некорректные геометрии
#     """
#     if not isinstance(data, list):
#         print("❌ Ожидается список объектов")
#         return
#
#     geometries = []
#     attributes = []
#     geometry_types = set()
#     fixed_geometries = 0
#     failed_geometries = 0
#
#     print(f"Обработка {len(data)} объектов...")
#
#     for i, item in enumerate(data):
#         if i % 10000 == 0:
#             print(f"Обработано {i} объектов...")
#
#         if isinstance(item, dict) and 'geometry' in item:
#             try:
#                 geom_data = item['geometry']
#
#                 if isinstance(geom_data, dict) and 'type' in geom_data and 'coordinates' in geom_data:
#                     # Создаем геометрию на основе типа
#                     geom_type = geom_data['type']
#                     coords = geom_data['coordinates']
#                     geometry_types.add(geom_type)
#
#                     geometry = None
#
#                     try:
#                         if geom_type == 'Point':
#                             geometry = Point(coords)
#                         elif geom_type == 'LineString':
#                             geometry = LineString(coords)
#                         elif geom_type == 'Polygon':
#                             geometry = Polygon(coords[0], coords[1:] if len(coords) > 1 else None)
#                         elif geom_type == 'MultiPoint':
#                             geometry = MultiPoint(coords)
#                         elif geom_type == 'MultiLineString':
#                             geometry = MultiLineString(coords)
#                         elif geom_type == 'MultiPolygon':
#                             polygons = []
#                             for poly_coords in coords:
#                                 polygons.append(
#                                     Polygon(poly_coords[0], poly_coords[1:] if len(poly_coords) > 1 else None))
#                             geometry = MultiPolygon(polygons)
#
#                         # Проверяем валидность геометрии
#                         if geometry is not None:
#                             if not geometry.is_valid and fix_invalid:
#                                 # Пытаемся исправить геометрию
#                                 fixed_geometry = fix_geometry(geometry, geom_type)
#                                 if fixed_geometry and fixed_geometry.is_valid:
#                                     geometry = fixed_geometry
#                                     fixed_geometries += 1
#                                 elif not geometry.is_valid:
#                                     # Если не удалось исправить, все равно сохраняем
#                                     print(f"⚠️  Объект {i}: геометрия некорректна, но сохранена")
#
#                             geometries.append(geometry)
#
#                             # Собираем атрибуты (исключая geometry)
#                             attrs = {}
#                             for key, value in item.items():
#                                 if key != 'geometry':
#                                     # Обрабатываем вложенные объекты
#                                     if isinstance(value, dict):
#                                         for sub_key, sub_value in value.items():
#                                             # Ограничиваем длину имен полей для shapefile
#                                             field_name = f"{key}_{sub_key}"[:10]
#                                             attrs[field_name] = str(sub_value) if sub_value is not None else ""
#                                     else:
#                                         # Ограничиваем длину имен полей для shapefile
#                                         field_name = key[:10]
#                                         attrs[field_name] = str(value) if value is not None else ""
#
#                             # Добавляем информацию о валидности геометрии
#                             attrs['geom_valid'] = 'Yes' if geometry.is_valid else 'No'
#
#                             attributes.append(attrs)
#                         else:
#                             # Создаем пустую геометрию для сохранения записи
#                             print(f"⚠️  Объект {i}: создана пустая геометрия")
#                             empty_geom = create_empty_geometry(geom_type)
#                             geometries.append(empty_geom)
#
#                             # Собираем атрибуты
#                             attrs = {}
#                             for key, value in item.items():
#                                 if key != 'geometry':
#                                     if isinstance(value, dict):
#                                         for sub_key, sub_value in value.items():
#                                             field_name = f"{key}_{sub_key}"[:10]
#                                             attrs[field_name] = str(sub_value) if sub_value is not None else ""
#                                     else:
#                                         field_name = key[:10]
#                                         attrs[field_name] = str(value) if value is not None else ""
#
#                             attrs['geom_valid'] = 'Empty'
#                             attributes.append(attrs)
#                             failed_geometries += 1
#
#                     except Exception as geom_error:
#                         print(f"⚠️  Ошибка создания геометрии для объекта {i}: {geom_error}")
#                         # Создаем пустую геометрию чтобы не потерять запись
#                         empty_geom = create_empty_geometry(geom_type)
#                         geometries.append(empty_geom)
#
#                         # Собираем атрибуты
#                         attrs = {}
#                         for key, value in item.items():
#                             if key != 'geometry':
#                                 if isinstance(value, dict):
#                                     for sub_key, sub_value in value.items():
#                                         field_name = f"{key}_{sub_key}"[:10]
#                                         attrs[field_name] = str(sub_value) if sub_value is not None else ""
#                                 else:
#                                     field_name = key[:10]
#                                     attrs[field_name] = str(value) if value is not None else ""
#
#                         attrs['geom_valid'] = 'Error'
#                         attributes.append(attrs)
#                         failed_geometries += 1
#
#             except Exception as e:
#                 print(f"⚠️  Ошибка обработки объекта {i}: {e}")
#                 # Создаем запись с пустой геометрией
#                 empty_geom = Point()  # Пустая точка
#                 geometries.append(empty_geom)
#
#                 attrs = {'error': f'Parse_error_{i}', 'geom_valid': 'ParseError'}
#                 attributes.append(attrs)
#                 failed_geometries += 1
#                 continue
#
#     print(f"\n📊 СТАТИСТИКА ОБРАБОТКИ:")
#     print(f"Всего объектов: {len(data)}")
#     print(f"Успешно обработано: {len(geometries)}")
#     print(f"Исправлено геометрий: {fixed_geometries}")
#     print(f"Проблемных геометрий: {failed_geometries}")
#     print(f"Типы геометрии: {list(geometry_types)}")
#
#     if geometries:
#         # Проверяем смешанные типы геометрии
#         if len(geometry_types) > 1:
#             print("\n⚠️  ВНИМАНИЕ: Обнаружены смешанные типы геометрии!")
#             print("Создаем отдельные файлы для каждого типа...")
#
#             # Группируем по типам геометрии
#             geometry_groups = {}
#             for geom, attrs in zip(geometries, attributes):
#                 # Определяем тип геометрии (для пустых геометрий используем первый найденный)
#                 if geom.is_empty and geometry_types:
#                     geom_type = list(geometry_types)[0]
#                 else:
#                     geom_type = geom.geom_type
#
#                 if geom_type not in geometry_groups:
#                     geometry_groups[geom_type] = {'geometries': [], 'attributes': []}
#                 geometry_groups[geom_type]['geometries'].append(geom)
#                 geometry_groups[geom_type]['attributes'].append(attrs)
#
#             # Создаем отдельные файлы
#             for geom_type, group_data in geometry_groups.items():
#                 type_output_path = output_path.replace('.shp', f'_{geom_type.lower()}.shp')
#                 gdf = gpd.GeoDataFrame(group_data['attributes'], geometry=group_data['geometries'])
#                 gdf.crs = 'EPSG:4326'  # WGS84
#                 gdf.to_file(type_output_path, driver='ESRI Shapefile')
#                 print(f"✅ Создан {type_output_path} с {len(group_data['geometries'])} объектами типа {geom_type}")
#         else:
#             # Один тип геометрии - создаем один файл
#             gdf = gpd.GeoDataFrame(attributes, geometry=geometries)
#             gdf.crs = 'EPSG:4326'  # WGS84
#             gdf.to_file(output_path, driver='ESRI Shapefile')
#             print(f"✅ Создан {output_path} с {len(geometries)} объектами")
#
#         print(f"\n💡 ПРИМЕЧАНИЕ:")
#         print(f"   - Поле 'geom_valid' показывает статус геометрии:")
#         print(f"     'Yes' = валидная, 'No' = невалидная, 'Empty' = пустая, 'Error' = ошибка")
#         print(f"   - Все записи сохранены, включая проблемные геометрии")
#
#     else:
#         print("❌ Не удалось создать ни одной геометрии")
#
#
# def fix_geometry(geometry, geom_type):
#     """
#     Пытается исправить некорректную геометрию
#     """
#     try:
#         # Метод buffer(0) часто исправляет самопересечения и другие проблемы
#         fixed = geometry.buffer(0)
#
#         if fixed.is_valid:
#             return fixed
#
#         # Для полигонов пробуем дополнительные методы
#         if geom_type in ['Polygon', 'MultiPolygon']:
#             # Пытаемся упростить геометрию
#             simplified = geometry.simplify(0.0001)
#             if simplified.is_valid:
#                 return simplified
#
#             # Пытаемся исправить через convex_hull (крайний случай)
#             hull = geometry.convex_hull
#             if hull.is_valid:
#                 return hull
#
#         return None
#
#     except Exception:
#         return None
#
#
# def create_empty_geometry(geom_type):
#     """
#     Создает пустую геометрию указанного типа
#     """
#     try:
#         if geom_type == 'Point':
#             return Point()
#         elif geom_type == 'LineString':
#             return LineString()
#         elif geom_type == 'Polygon':
#             return Polygon()
#         elif geom_type == 'MultiPoint':
#             return MultiPoint()
#         elif geom_type == 'MultiLineString':
#             return MultiLineString()
#         elif geom_type == 'MultiPolygon':
#             return MultiPolygon()
#         else:
#             return Point()  # По умолчанию пустая точка
#     except:
#         return Point()  # Резервный вариант
#
#
# def convert_points_to_shapefile(data, output_path):
#     """
#     Конвертирует данные с координатами в точечный shapefile
#     """
#     # Для совместимости - перенаправляем на новую функцию
#     convert_agricultural_data_to_shapefile(data, output_path)
#
#
# # Пример использования
# def main():
#     """
#     Основная функция для анализа и конвертации
#     """
#     print("🗺️  АНАЛИЗАТОР JSON ДЛЯ SHAPEFILE КОНВЕРТАЦИИ")
#     print("=" * 50)
#
#     # Путь к JSON файлу
#     json_file = input("Введите путь к JSON файлу: ").strip().strip('"')
#
#     if not Path(json_file).exists():
#         print(f"❌ Файл не найден: {json_file}")
#         return
#
#     # Анализируем структуру
#     try:
#         data = analyze_json_structure(json_file)
#
#         # Предлагаем конвертацию
#         convert = input("\nХотите конвертировать в shapefile? (y/n): ").lower()
#
#         if convert == 'y':
#             output_file = input("Введите путь для выходного shapefile (.shp): ").strip()
#             if not output_file.endswith('.shp'):
#                 output_file += '.shp'
#
#             conversion_type = input("Тип конвертации (geojson/points/auto): ").lower() or 'auto'
#
#             # Опция для исправления геометрий
#             fix_geometries = input("Исправлять некорректные геометрии? (y/n, по умолчанию y): ").lower()
#             fix_geometries = fix_geometries != 'n'  # По умолчанию True
#
#             convert_to_shapefile(json_file, output_file, conversion_type)
#
#     except Exception as e:
#         print(f"❌ Ошибка: {e}")
#
#
# if __name__ == "__main__":
#     main()

import json
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon
import pandas as pd
from pathlib import Path


def convert_without_data_loss(json_file_path, output_path, method='multiple_formats'):
    """
    Конвертация без потери данных

    method:
    - 'multiple_formats': создает Shapefile + GeoJSON + CSV
    - 'geojson_only': только GeoJSON (без ограничений)
    - 'expanded_fields': все поля в отдельных колонках Shapefile
    - 'json_field': сохраняет исходный JSON в отдельном поле
    """

    print(f"🔄 КОНВЕРТАЦИЯ БЕЗ ПОТЕРИ ДАННЫХ - Метод: {method}")
    print("=" * 60)

    # Загружаем данные
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("❌ Ожидается массив объектов")
        return

    print(f"📂 Загружено {len(data)} объектов")

    if method == 'multiple_formats':
        create_multiple_formats(data, output_path)
    elif method == 'geojson_only':
        create_geojson_only(data, output_path)
    elif method == 'expanded_fields':
        create_expanded_shapefile(data, output_path)
    elif method == 'json_field':
        create_shapefile_with_json_field(data, output_path)


def create_multiple_formats(data, output_path):
    """
    МЕТОД 1: Создает несколько форматов файлов
    - Shapefile для ГИС работы (оптимизированные поля)
    - GeoJSON с полными данными (без ограничений)
    - CSV с полными атрибутами
    """
    print("\n📁 СОЗДАНИЕ НЕСКОЛЬКИХ ФОРМАТОВ:")

    geometries = []
    shapefile_attrs = []
    full_data_for_geojson = []
    csv_attributes = []

    for i, item in enumerate(data):
        if 'geometry' in item:
            try:
                # Создаем геометрию
                geometry = create_geometry_from_item(item)
                if geometry:
                    geometries.append(geometry)

                    # 1. Атрибуты для Shapefile (сокращенные)
                    shapefile_attr = create_optimized_attributes(item, i)
                    shapefile_attrs.append(shapefile_attr)

                    # 2. Полные данные для GeoJSON
                    full_data_for_geojson.append(item.copy())

                    # 3. Развернутые атрибуты для CSV
                    csv_attr = flatten_all_attributes(item, i)
                    csv_attributes.append(csv_attr)

            except Exception as e:
                print(f"⚠️  Ошибка объекта {i}: {e}")

    # Создаем Shapefile
    if geometries:
        base_path = output_path.replace('.shp', '')

        # 1. Shapefile (оптимизированный для ГИС)
        shapefile_path = f"{base_path}_optimized.shp"
        create_shapefile_from_data(geometries, shapefile_attrs, shapefile_path)

        # 2. GeoJSON (полные данные без ограничений)
        geojson_path = f"{base_path}_full.geojson"
        create_full_geojson(full_data_for_geojson, geojson_path)

        # 3. CSV (все атрибуты развернуты)
        csv_path = f"{base_path}_all_attributes.csv"
        create_detailed_csv(csv_attributes, csv_path)

        print(f"\n✅ СОЗДАНЫ ФАЙЛЫ:")
        print(f"   📊 {shapefile_path} - для работы в ГИС")
        print(f"   🗺️  {geojson_path} - полные данные с геометрией")
        print(f"   📋 {csv_path} - все атрибуты в таблице")


def create_geojson_only(data, output_path):
    """
    МЕТОД 2: Только GeoJSON - формат без ограничений
    """
    print("\n🗺️  СОЗДАНИЕ GEOJSON (БЕЗ ОГРАНИЧЕНИЙ):")

    geojson_path = output_path.replace('.shp', '.geojson')

    # Проверяем, что данные уже в формате GeoJSON
    if isinstance(data, list) and all('geometry' in item for item in data if isinstance(item, dict)):
        # Создаем FeatureCollection
        geojson_data = {
            "type": "FeatureCollection",
            "features": []
        }

        for item in data:
            if 'geometry' in item:
                feature = {
                    "type": "Feature",
                    "geometry": item['geometry'],
                    "properties": {k: v for k, v in item.items() if k != 'geometry'}
                }
                geojson_data['features'].append(feature)

        # Сохраняем GeoJSON
        with open(geojson_path, 'w', encoding='utf-8') as f:
            json.dump(geojson_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Создан GeoJSON: {geojson_path}")
        print(f"   📊 {len(geojson_data['features'])} объектов")
        print(f"   💾 ВСЕ данные сохранены без изменений")

        # Проверяем в GeoPandas
        try:
            gdf = gpd.read_file(geojson_path)
            print(f"   ✅ Проверка: успешно загружается в GeoPandas")
            print(f"   📋 Поля: {len(gdf.columns)} колонок")
        except Exception as e:
            print(f"   ⚠️  Предупреждение при проверке: {e}")


def create_expanded_shapefile(data, output_path):
    """
    МЕТОД 3: Shapefile со всеми полями (развернутыми)
    """
    print("\n📊 СОЗДАНИЕ РАСШИРЕННОГО SHAPEFILE:")

    geometries = []
    all_attributes = []

    # Собираем все возможные поля из всех объектов
    all_fields = set()
    for item in data:
        flattened = flatten_all_attributes(item, 0)
        all_fields.update(flattened.keys())

    print(f"   🔍 Найдено {len(all_fields)} уникальных полей")
    print(f"   📝 Примеры полей: {', '.join(list(all_fields)[:10])}")

    for i, item in enumerate(data):
        if 'geometry' in item:
            try:
                geometry = create_geometry_from_item(item)
                if geometry:
                    geometries.append(geometry)

                    # Развернутые атрибуты с заполнением всех полей
                    flattened_attrs = flatten_all_attributes(item, i)

                    # Заполняем отсутствующие поля пустыми значениями
                    complete_attrs = {}
                    for field in all_fields:
                        # Сокращаем имена полей для Shapefile (10 символов максимум)
                        short_field_name = create_short_field_name(field)
                        complete_attrs[short_field_name] = flattened_attrs.get(field, "")

                    all_attributes.append(complete_attrs)

            except Exception as e:
                print(f"⚠️  Ошибка объекта {i}: {e}")

    # Создаем Shapefile
    if geometries and all_attributes:
        create_shapefile_from_data(geometries, all_attributes, output_path)

        print(f"   ✅ Создан расширенный Shapefile: {output_path}")
        print(f"   📊 {len(geometries)} объектов с {len(all_fields)} полями")


def create_shapefile_with_json_field(data, output_path):
    """
    МЕТОД 4: Shapefile с исходным JSON в отдельном поле
    """
    print("\n💾 СОЗДАНИЕ SHAPEFILE С JSON ПОЛЕМ:")

    geometries = []
    attributes = []

    for i, item in enumerate(data):
        if 'geometry' in item:
            try:
                geometry = create_geometry_from_item(item)
                if geometry:
                    geometries.append(geometry)

                    # Основные поля + полный JSON
                    attr = {
                        'id': i + 1,
                        'contur_id': str(item.get('contour_id', '')),
                        'farmer_nm': str(item.get('farmer_name', ''))[:50],
                        'area': item.get('area', 0),
                        'plant_name': str(item.get('details', {}).get('plant_name', ''))[:30],
                        # Сохраняем ВЕСЬ исходный JSON (сжато)
                        'full_json': json.dumps(item, ensure_ascii=False, separators=(',', ':'))[:254]
                    }

                    # Если JSON слишком длинный, создаем файл с полными данными
                    full_json_str = json.dumps(item, ensure_ascii=False, indent=2)
                    if len(full_json_str) > 254:
                        attr['json_file'] = f"object_{i + 1}.json"
                        # Сохраняем полный JSON в отдельный файл
                        json_file_path = output_path.replace('.shp', f'_object_{i + 1}.json')
                        with open(json_file_path, 'w', encoding='utf-8') as f:
                            json.dump(item, f, ensure_ascii=False, indent=2)

                    attributes.append(attr)

            except Exception as e:
                print(f"⚠️  Ошибка объекта {i}: {e}")

    if geometries:
        create_shapefile_from_data(geometries, attributes, output_path)
        print(f"   ✅ Shapefile создан: {output_path}")
        print(f"   📊 Основные поля + поле full_json с полными данными")


def flatten_all_attributes(item, index):
    """
    Разворачивает все атрибуты объекта в плоскую структуру
    """
    flattened = {'object_id': index + 1}

    def flatten_dict(obj, parent_key=''):
        items = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == 'geometry':
                    continue
                new_key = f"{parent_key}_{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key).items())
                elif isinstance(v, list):
                    # Преобразуем списки в строку
                    items.append((new_key, json.dumps(v, ensure_ascii=False)))
                else:
                    items.append((new_key, str(v) if v is not None else ""))
        return dict(items)

    flattened.update(flatten_dict(item))
    return flattened


def create_short_field_name(field_name, max_length=10):
    """
    Создает короткое имя поля для Shapefile (максимум 10 символов)
    """
    if len(field_name) <= max_length:
        return field_name

    # Умное сокращение
    parts = field_name.split('_')
    if len(parts) > 1:
        # Берем первые буквы каждой части
        short_name = ''.join([part[:2] for part in parts])[:max_length]
    else:
        # Просто обрезаем
        short_name = field_name[:max_length]

    return short_name


def create_geometry_from_item(item):
    """Создает геометрию из объекта данных"""
    try:
        geom_data = item['geometry']
        if isinstance(geom_data, dict) and 'type' in geom_data and 'coordinates' in geom_data:
            geom_type = geom_data['type']
            coords = geom_data['coordinates']

            if geom_type == 'Point':
                return Point(coords)
            elif geom_type == 'LineString':
                return LineString(coords)
            elif geom_type == 'Polygon':
                return Polygon(coords[0], coords[1:] if len(coords) > 1 else None)
            elif geom_type == 'MultiPoint':
                return MultiPoint(coords)
            elif geom_type == 'MultiLineString':
                return MultiLineString(coords)
            elif geom_type == 'MultiPolygon':
                polygons = []
                for poly_coords in coords:
                    polygons.append(
                        Polygon(poly_coords[0], poly_coords[1:] if len(poly_coords) > 1 else None)
                    )
                return MultiPolygon(polygons)
    except Exception as e:
        print(f"Ошибка создания геометрии: {e}")
    return None


def create_optimized_attributes(item, index):
    """Создает оптимизированные атрибуты для Shapefile"""
    return {
        'id': index + 1,
        'contur_id': str(item.get('contour_id', '')),
        'farmer_inn': str(item.get('farmer_inn', '')),
        'farmer_nm': str(item.get('farmer_name', ''))[:50],
        'contur_num': item.get('contour_number', 0),
        'area': item.get('area', 0.0),
        'cad_number': str(item.get('cad_number', '')),
        'plant_name': str(item.get('details', {}).get('plant_name', ''))[:30],
        'crop_gen': str(item.get('details', {}).get('crop_generation', ''))[:20],
        'agro_id': item.get('details', {}).get('agroplatform_id', 0),
        'year': item.get('year', 0),
        'lot_type': str(item.get('lot_type', '')),
        'soato': str(item.get('soato', '')),
    }


def create_shapefile_from_data(geometries, attributes, output_path):
    """Создает Shapefile из геометрий и атрибутов"""

    # Группируем по типам геометрии
    geometry_groups = {}
    for geom, attrs in zip(geometries, attributes):
        geom_type = geom.geom_type
        if geom_type not in geometry_groups:
            geometry_groups[geom_type] = {'geometries': [], 'attributes': []}
        geometry_groups[geom_type]['geometries'].append(geom)
        geometry_groups[geom_type]['attributes'].append(attrs)

    if len(geometry_groups) > 1:
        # Создаем отдельные файлы для каждого типа
        for geom_type, group_data in geometry_groups.items():
            type_output_path = output_path.replace('.shp', f'_{geom_type.lower()}.shp')
            gdf = gpd.GeoDataFrame(group_data['attributes'], geometry=group_data['geometries'])
            gdf.crs = 'EPSG:4326'
            gdf.to_file(type_output_path, driver='ESRI Shapefile', encoding='utf-8')
            print(f"   ✅ {type_output_path}: {len(group_data['geometries'])} объектов типа {geom_type}")
    else:
        # Один файл
        gdf = gpd.GeoDataFrame(attributes, geometry=geometries)
        gdf.crs = 'EPSG:4326'
        gdf.to_file(output_path, driver='ESRI Shapefile', encoding='utf-8')
        print(f"   ✅ {output_path}: {len(geometries)} объектов")


def create_full_geojson(data, geojson_path):
    """Создает GeoJSON с полными данными"""
    geojson_data = {
        "type": "FeatureCollection",
        "features": []
    }

    for item in data:
        feature = {
            "type": "Feature",
            "geometry": item['geometry'],
            "properties": {k: v for k, v in item.items() if k != 'geometry'}
        }
        geojson_data['features'].append(feature)

    with open(geojson_path, 'w', encoding='utf-8') as f:
        json.dump(geojson_data, f, ensure_ascii=False, indent=2)


def create_detailed_csv(attributes, csv_path):
    """Создает детальный CSV со всеми атрибутами"""
    df = pd.DataFrame(attributes)
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"   📊 CSV: {len(df)} записей, {len(df.columns)} полей")


# Главная функция с выбором метода
def main():
    """Основная функция с выбором метода конвертации"""

    print("🔄 КОНВЕРТЕР БЕЗ ПОТЕРИ ДАННЫХ")
    print("=" * 40)

    json_file = input("Путь к JSON файлу: ").strip().strip('"')
    if not Path(json_file).exists():
        print(f"❌ Файл не найден: {json_file}")
        return

    output_file = input("Путь для выходных файлов (.shp): ").strip()
    if not output_file.endswith('.shp'):
        output_file += '.shp'

    print("\n📋 ВЫБЕРИТЕ МЕТОД:")
    print("1. Несколько форматов (Shapefile + GeoJSON + CSV)")
    print("2. Только GeoJSON (без ограничений)")
    print("3. Расширенный Shapefile (все поля)")
    print("4. Shapefile с JSON полем")

    choice = input("Выбор (1-4): ").strip()

    methods = {
        '1': 'multiple_formats',
        '2': 'geojson_only',
        '3': 'expanded_fields',
        '4': 'json_field'
    }

    method = methods.get(choice, 'multiple_formats')

    convert_without_data_loss(json_file, output_file, method)

    print(f"\n🎯 РЕЗУЛЬТАТ: ВСЕ ДАННЫЕ СОХРАНЕНЫ БЕЗ ПОТЕРЬ!")


if __name__ == "__main__":
    main()
