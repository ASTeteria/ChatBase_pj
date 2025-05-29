document.addEventListener('DOMContentLoaded', function() {
    let chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || [];

    // Сохраняем сообщение
    function saveMessage(message, isUser) {
        chatHistory.push({ text: message, isUser: isUser });
        localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
        console.log('Saved to chatHistory:', chatHistory); // Логируем историю
    }

    // Отправляем запрос в API
    async function searchArticles(query) {
        try {
            const csrfToken = getCsrfToken();
            console.log('CSRF Token:', csrfToken); // Логируем CSRF-токен
            // Нормализуем запрос
            let normalizedQuery = query
                .replace(/статті/gi, 'articles')
                .replace(/про/gi, 'about');
            console.log('Normalized Query:', normalizedQuery); // Логируем нормализованный запрос
            const response = await fetch('/api/search/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({ query: normalizedQuery }),
            });
            console.log('Search Response Status:', response.status); // Логируем статус
            const data = await response.json();
            console.log('Search Response Data:', data); // Логируем данные
            return data.response || "Вибачте, щось пішло не так.";
        } catch (error) {
            console.error('Помилка пошуку:', error);
            return "Помилка під час пошуку статей.";
        }
    }

    // Получаем CSRF-токен
    function getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') return value;
        }
        console.warn('CSRF-токен не знайдено');
        return '';
    }

    // Перехватываем сообщения от Chatbase
    window.addEventListener('message', async function(event) {
        if (event.origin !== 'https://www.chatbase.co') return; // Проверяем источник
        console.log('Chatbase Event:', JSON.stringify(event.data, null, 2)); // Логируем событие
        if (event.data?.type === 'user-message') {
            const query = event.data.data?.content; // Извлекаем content
            console.log('Query:', query); // Логируем запрос
            if (query && typeof query === 'string') {
                saveMessage(query, true); // Сохраняем запрос
                const response = await searchArticles(query); // Вызываем поиск
                saveMessage(response, false); // Сохраняем ответ
                // Отправляем ответ в чатбот
                const iframe = document.querySelector('iframe[src*="chatbase.co"]');
                if (iframe) {
                    console.log('Sending response to iframe:', response); // Логируем отправку
                    // Отправляем немедленно
                    iframe.contentWindow.postMessage(
                        { type: 'assistant-message', data: { content: response } },
                        'https://www.chatbase.co'
                    );
                    iframe.contentWindow.postMessage(
                        { message: response },
                        'https://www.chatbase.co'
                    );
                } else {
                    console.warn('Iframe не знайдено');
                }
            } else {
                console.warn('Невірний формат запиту:', JSON.stringify(event.data.data, null, 2));
            }
        }
    });
});