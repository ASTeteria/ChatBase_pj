document.addEventListener('DOMContentLoaded', function() {
    let chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || [];

    // Сохраняем сообщение
    function saveMessage(message, isUser) {
        chatHistory.push({ text: message, isUser: isUser });
        localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
    }

    // Отправляем запрос в API
    async function searchArticles(query) {
        try {
            const response = await fetch('/api/search/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify({ query: query }),
            });
            const data = await response.json();
            return data.response || "Sorry, something went wrong.";
        } catch (error) {
            console.error('Search error:', error);
            return "Error searching articles.";
        }
    }

    // Получаем CSRF-токен
    function getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') return value;
        }
        return '';
    }

    // Перехватываем сообщения от Chatbase
    window.addEventListener('message', async function(event) {
        if (event.origin !== 'https://www.chatbase.co') return; // Проверяем источник
        const message = event.data?.content; // Предполагаем формат { content: "..." }
        if (message && typeof message === 'string') {
            saveMessage(message, true); // Сохраняем запрос пользователя
            const response = await searchArticles(message); // Вызываем поиск
            saveMessage(response, false); // Сохраняем ответ
            // Отправляем ответ в чатбот
            const iframe = document.querySelector('iframe[src*="chatbase.co"]');
            if (iframe) {
                iframe.contentWindow.postMessage({ content: response }, 'https://www.chatbase.co');
            }
        }
    });
});