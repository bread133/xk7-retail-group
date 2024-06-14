import hashlib

def generate_hashes(pairs):
    """
    Функция для формирования хэш слепка для пар точек.
    
    Параметры:
    - pairs: список пар точек с ((t1, f1), (t2, f2))
    
    Возвращает:
    - pairs: спиок хэш сплепков для каждой пары и время якороной точки A
    """
    hashes = []
    for pair in pairs:
        point_А, point_B = pair
        time_A, freq_A = point_А
        time_B, freq_B = point_B
        
        # Формирование ключа из частот и разницы времени
        key = f"{freq_A}-{freq_B}-{time_B - time_A}"

        
        # Создание хэша
        hash_object = hashlib.sha256(key.encode())
        hash_hex = hash_object.hexdigest()
        '''
        Место для вставки в запрос
        '''
        hashes.append((hash_hex, time_A))
    
    return hashes