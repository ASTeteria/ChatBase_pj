document.addEventListener('DOMContentLoaded', function() {
    let chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || [];


    function saveMessage(message, isUser) {
        chatHistory.push({ text: message, isUser: isUser });
        localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
        console.log('Saved to chatHistory:', chatHistory);
    }


    async function searchArticles(query) {
        try {
            const csrfToken = getCsrfToken();
            console.log('CSRF Token:', csrfToken);
            const response = await fetch('/api/search/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({ query: query }),
            });
            console.log('Search Response Status:', response.status);
            const data = await response.json();
            console.log('Search Response Data:', data);
            return data.response || "Вибачте, щось пішло не так.";
        } catch (error) {
            console.error('Помилка пошуку:', error);
            return "Помилка під час пошуку статей.";
        }
    }


    function getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') return value;
        }
        console.warn('CSRF-токен не знайдено');
        return '';
    }


    window.addEventListener('message', async function(event) {
        if (event.origin !== 'https://www.chatbase.co') return;
        console.log('Chatbase Event:', JSON.stringify(event.data, null, 2));
        if (event.data?.type === 'user-message') {
            const query = event.data.data?.content;
            console.log('Query:', query);
            if (query && typeof query === 'string') {
                saveMessage(query, true);
                const response = await searchArticles(query);
                saveMessage(response, false);

                const iframe = document.querySelector('iframe[src*="chatbase.co"]');
                if (iframe) {
                    console.log('Sending response to iframe:', response); // Логируем
                    iframe.contentWindow.postMessage(
                        { type: 'assistant-message', data: { content: response } },
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