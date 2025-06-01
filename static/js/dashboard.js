
(function ($) {
    $(document).ready(function () {
        // Проверка загрузки jQuery
        if (typeof $ === 'undefined') {
            console.error('[Dashboard] jQuery not loaded.');
            return;
        }
        console.log('[Dashboard] Script loaded.');

        // CSRF-токен
        function getCsrfToken() {
            const token = $('meta[name="csrf-token"]').attr('content');
            if (!token) {
                console.error('[Dashboard] CSRF token not found.');
            }
            return token;
        }

        // Генерация нового агента
        $('#generate-agent-btn').on('click', function () {
            console.log('[Dashboard] Generating new agent...');
            const csrfToken = getCsrfToken();
            if (!csrfToken) return;

            $.ajax({
                url: '/api/generate-agent/',
                type: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                dataType: 'json',
                success: function (response) {
                    console.log('[Dashboard] Agent generated:', response);
                    const agentId = response.agent_id;
                    // Добавляем новую рамку
                    const newAgentBox = $('<div>', {
                        class: 'agent-id-box',
                        'data-agent-id': agentId,
                        text: `Agent ID: ${agentId}`,
                    });
                    $('#agent-id-container').prepend(newAgentBox);

                    // Обновляем список агентов
                    const newAgentItem = $('<li>', {
                        'data-agent-id': agentId,
                        html: `Agent for ${$('body').data('username')} (ID: ${agentId}) - Created: ${new Date().toLocaleString()}` +
                              `<button class="delete-agent-btn" data-agent-id="${agentId}">Delete</button>`,
                    });
                    $('#agent-list').prepend(newAgentItem);

                    // Удаляем сообщение "No active agents"
                    $('#agent-id-container .card').remove();

                    // Прокрутка к новому agent_id
                    $('html, body').animate({
                        scrollTop: newAgentBox.offset().top - 100,
                    }, 500);
                },
                error: function (xhr) {
                    console.error('[Dashboard] Generate agent error:', xhr.status, xhr.responseJSON?.error || 'Unknown error');
                    alert('Failed to generate agent: ' + (xhr.responseJSON?.error || 'Unknown error'));
                },
            });
        });

        // Удаление агента
        $(document).on('click', '.delete-agent-btn', function () {
            const agentId = $(this).data('agent-id');
            console.log('[Dashboard] Deleting agent:', agentId);
            if (!confirm(`Are you sure you want to delete agent ${agentId}?`)) return;

            const csrfToken = getCsrfToken();
            if (!csrfToken) return;

            $.ajax({
                url: '/api/delete-agent/',
                type: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                data: {
                    agent_id: agentId,
                },
                dataType: 'json',
                success: function (response) {
                    console.log('[Dashboard] Agent deleted:', agentId);
                    // Удаляем agent_id из UI
                    $(`[data-agent-id="${agentId}"]`).remove();

                    // Если агентов не осталось
                    if ($('#agent-list li').length === 0) {
                        $('#agent-id-container').html(
                            '<div class="card"><p>No active agents. Generate one above!</p></div>'
                        );
                    }
                },
                error: function (xhr) {
                    console.error('[Dashboard] Delete agent error:', xhr.status, xhr.responseJSON?.error || 'Unknown error');
                    alert('Failed to delete agent: ' + (xhr.responseJSON?.error || 'Unknown error'));
                },
            });
        });
    });
})(jQuery);
