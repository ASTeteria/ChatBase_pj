document.addEventListener('DOMContentLoaded', function() {
    let chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || [];

    // Сохраняем сообщение
    function saveMessage(message, isUser) {
        chatHistory.push({ text: message, isUser: isUser });
        localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
        showMessages();
    }

    // Показываем сообщения
    function showMessages() {
        const chatBox = document.querySelector('.chat-messages');
        if (chatBox) {
            chatBox.innerHTML = '';
            chatHistory.forEach(msg => {
                const div = document.createElement('div');
                div.textContent = `${msg.isUser ? 'You' : 'Bot'}: ${msg.text}`;
                chatBox.appendChild(div);
            });
            chatBox.scrollTop = chatBox.scrollHeight;
        }
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

    // Перехватываем сообщения чатбота
    window.addEventListener('chatbaseMessage', async function(event) {
        const message = event.detail?.message;
        if (message) {
            saveMessage(message, false);
        }
    });

    // Перехватываем отправку сообщений
    window.addEventListener('chatbaseSendMessage', async function(event) {
        const query = event.detail?.message;
        if (query) {
            saveMessage(query, true);
            const response = await searchArticles(query);
            saveMessage(response, false);
        }
    });

    showMessages();
});