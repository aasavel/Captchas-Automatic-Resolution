"""
ПРИМЕР ИНТЕГРАЦИИ С МОДЕЛЬЮ OCR/VLM
Показывает как подключить твою модель распознавания к solver'у
"""

from captcha_solver import CaptchaSolver
import time

# ============================================
# ВАРИАНТ 1: С МОДЕЛЬЮ (когда она будет готова)
# ============================================

def solve_with_model_example():
    """
    Пример с настоящей моделью OCR/VLM
    (раскомментируй когда модель будет готова)
    """
    
    # from your_model import CaptchaOCR  # ← Твоя модель
    # model = CaptchaOCR()
    
    solver = CaptchaSolver()
    
    url = "https://2captcha.com/demo/normal"
    
    # Загружаем страницу
    solver.driver.get(url)
    time.sleep(2)
    
    # Находим капчу
    solver.try_click_consent_buttons()
    elements = solver.driver.find_elements_by_xpath("//img | //canvas")
    captcha = solver.find_captcha_in_elements(elements)
    
    if captcha:
        # Сохраняем картинку
        captcha.screenshot("temp_captcha.png")
        
        # ВЫЗЫВАЕМ МОДЕЛЬ
        # solution = model.predict("temp_captcha.png")  # ← Тут будет твоя модель
        solution = "СИМУЛЯЦИЯ"  # Пока заглушка
        
        print(f"Модель распознала: {solution}")
        
        # Автоматически заполняем и отправляем
        solver.find_captcha_input_field()
        solver.fill_captcha_solution(solution)
        solver.submit_captcha()
        
        # Проверяем результат
        success = solver.check_captcha_success()
        print(f"Результат: {'✓ УСПЕХ' if success else '✗ ОШИБКА'}")
    
    solver.close()


# ============================================
# ВАРИАНТ 2: СИМУЛЯЦИЯ БЕЗ МОДЕЛИ (для теста)
# ============================================

def solve_with_hardcoded_solutions():
    """
    Симуляция работы с моделью - просто передаём готовые решения
    Используй это СЕЙЧАС для тестов
    """
    
    solver = CaptchaSolver()
    
    # Список URL и их решений (для теста вводишь вручную один раз)
    test_cases = [
        {
            "url": "https://2captcha.com/demo/normal",
            "solution": "ABC123"  # ← Тут подставь настоящее решение
        },
        {
            "url": "https://www.mtcaptcha.com/test-multiple-captcha", 
            "solution": "XYZ789"  # ← И тут
        }
    ]
    
    for idx, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"ТЕСТ {idx}/{len(test_cases)}")
        print(f"{'='*60}")
        
        result = solver.solve_captcha_complete(
            url=test["url"],
            solution=test["solution"]  # ← АВТОМАТИЧЕСКИ передаём решение
        )
        
        print(f"\nРезультат теста {idx}:")
        print(f"  Капча найдена: {result['captcha_found']}")
        print(f"  Поле найдено: {result['input_found']}")
        print(f"  Заполнено: {result['solution_filled']}")
        print(f"  Отправлено: {result['submitted']}")
        print(f"  Успех: {result['success']}")
        
        time.sleep(2)
    
    solver.close()
    print("\n✓ Все тесты завершены!")


# ============================================
# ВАРИАНТ 3: ПОЛНАЯ АВТОМАТИЗАЦИЯ С МОДЕЛЬЮ
# ============================================

def full_automated_workflow():
    """
    Полностью автоматический workflow
    Это то, как будет работать в финальной версии
    """
    
    # from your_model import predict_captcha  # ← Твоя модель
    
    solver = CaptchaSolver()
    urls = [
        "https://2captcha.com/demo/normal",
        "https://rutracker.org/forum/profile.php?mode=register",
    ]
    
    results = []
    
    for url in urls:
        print(f"\n{'='*60}")
        print(f"Обработка: {url}")
        print(f"{'='*60}")
        
        # Загружаем и находим капчу
        solver.driver.get(url)
        time.sleep(2)
        solver.try_click_consent_buttons()
        
        elements = solver.driver.find_elements_by_xpath("//img | //canvas")
        captcha = solver.find_captcha_in_elements(elements)
        
        if captcha:
            # Сохраняем картинку
            captcha.screenshot("current_captcha.png")
            
            # ========================================
            # ВЫЗОВ МОДЕЛИ (когда будет готова)
            # ========================================
            # solution = predict_captcha("current_captcha.png")
            
            # Пока симуляция
            solution = "TEST123"  # ← ЗАМЕНИТЬ НА model.predict()
            
            print(f"Решение от модели: {solution}")
            
            # Автоматически заполняем
            solver.find_captcha_input_field()
            solver.fill_captcha_solution(solution)
            solver.submit_captcha()
            
            # Проверяем
            success = solver.check_captcha_success()
            
            results.append({
                'url': url,
                'solution': solution,
                'success': success
            })
        
        time.sleep(2)
    
    solver.close()
    
    # Итоговый отчёт
    print("\n" + "="*60)
    print("ИТОГОВЫЙ ОТЧЁТ")
    print("="*60)
    for r in results:
        status = "✓" if r['success'] else "✗"
        print(f"{status} {r['url']}: {r['solution']}")
    print("="*60)


# ============================================
# ГЛАВНАЯ ФУНКЦИЯ - ВЫБОР ВАРИАНТА
# ============================================

def main():
    print("\n" + "="*60)
    print("ВЫБЕРИ ВАРИАНТ ТЕСТА:")
    print("="*60)
    print("1. С хардкоженными решениями (для теста СЕЙЧАС)")
    print("2. С моделью (когда она будет готова)")
    print("3. Полная автоматизация (финальная версия)")
    
    choice = input("\nТвой выбор (1/2/3): ").strip()
    
    if choice == "1":
        print("\n✓ Запускаем с готовыми решениями...")
        solve_with_hardcoded_solutions()
    
    elif choice == "2":
        print("\n✓ Запускаем с моделью...")
        solve_with_model_example()
    
    elif choice == "3":
        print("\n✓ Запускаем полную автоматизацию...")
        full_automated_workflow()
    
    else:
        print("Неверный выбор!")


if __name__ == "__main__":
    main()
