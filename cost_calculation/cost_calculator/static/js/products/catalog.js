function checkProductExists(name, callback) {
    $.ajax({
        url: "/products/check-exists/",
        type: "GET",
        data: { 'name': name},
        success: function(response) {
            callback(response.exists);
        },
        error: function() {
            callback(false);
        }
    });
}

$(document).ready(function() {
    $('#add-product-btn').click(function() {
        const name = $('#id_name').val();

        checkProductExists(name, function(exists) {
            if (exists) {
                showErrors({ name: ["Продукт с таким названием уже существует!"] });
                return false;
            }

            const totalPrice = $('#id_total_price').val();
            const totalQuantity = $('#id_total_quantity').val();
            const unitId = $('#id_unit').val();

            $.ajax({
                url: "/products/create/",
                type: "POST",
                data: {
                    'name': name,
                    'total_price': totalPrice,
                    'total_quantity': totalQuantity,
                    'unit': unitId,
                    'csrfmiddlewaretoken': getCookie('csrftoken')
                },
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                success: function(response) {
                    // Добавляем новый продукт в начало таблицы
                    $('#product-table tbody').prepend(`
                        <tr id="product-${response.id}">
                            <td>${response.name}</td>
                            <td>${parseFloat(response.total_price).toFixed(2)}</td>
                            <td>${parseFloat(response.total_quantity).toFixed(2)}</td>
                            <td>${response.unit}</td>
                            <td>
                                <button class="edit-product-btn btn btn-success" data-id="${response.id}">
                                    <i class="bi bi-pencil"></i> Изменить
                                </button>
                                <button class="delete-product-btn btn btn-success" data-id="${response.id}">
                                    <i class="bi bi-trash"></i> Удалить
                                </button>
                            </td>
                        </tr>
                    `);

                    // Очищаем форму
                    $('#id_name').val('');
                    $('#id_total_price').val('');
                    $('#id_total_quantity').val('');
                },
                error: function(response) {
                    if (response.responseJSON && response.responseJSON.error) {
                        showErrors(response.responseJSON.error);
                    }
                }
            });
        });
    });

    // 2. Редактирование продукта
    $(document).on('click', '.edit-product-btn', function() {
        const $btn = $(this);
        const $row = $btn.closest('tr');
        const productId = $btn.data('id');


        if ($btn.hasClass('save-mode')) {
            // Режим сохранения
            const name = $row.find('.edit-name').val();
            const originalName = $row.data('name');

            // Проверяем только если имя изменилось
            if (name !== originalName) {
                checkProductExists(name, productId, function(exists) {
                    if (exists) {
                        showErrors({ name: ["Продукт с таким названием уже существует!"] });
                        return false;
                    }
                    saveProductChanges($row, productId);
                });
            } else {
                saveProductChanges($row, productId);
            }
        } else {
            // Режим редактирования
            const originalName = $row.data('name');
            const originalPrice = $row.data('price');
            const originalQuantity = $row.data('quantity');
            const originalUnitId = $row.data('unit-id');

            // Получаем список единиц измерения из формы добавления
            const unitOptions = $('#id_unit').html();

            $row.html(`
                <td><input type="text" class="form-control edit-name" value="${originalName}"></td>
                <td><input type="number" step="0.01" class="form-control edit-price" value="${originalPrice}"></td>
                <td><input type="number" step="0.01" class="form-control edit-quantity" value="${originalQuantity}"></td>
                <td>
                    <select class="form-control edit-unit">
                        ${unitOptions}
                    </select>
                </td>
                <td>
                    <button class="edit-product-btn btn btn-success save-mode" data-id="${productId}">
                        <i class="bi bi-check"></i> Сохранить
                    </button>
                    <button class="cancel-edit-btn btn btn-secondary" data-id="${productId}">
                        <i class="bi bi-x"></i> Отмена
                    </button>
                </td>
            `);

            $row.find('.edit-unit').val(originalUnitId);
        }
    });

    // Отмена редактирования
    $(document).on('click', '.cancel-edit-btn', function() {
        const $btn = $(this);
        const $row = $btn.closest('tr');
        const productId = $btn.data('id');

        // Восстанавливаем оригинальные значения
        $row.html(`
            <td>${$row.data('name')}</td>
            <td>${$row.data('price')}</td>
            <td>${$row.data('quantity')}</td>
            <td>${$row.data('unit-name')}</td>
            <td>
                <button class="edit-product-btn btn btn-success" data-id="${productId}">
                    <i class="bi bi-pencil"></i> Изменить
                </button>
                <button class="delete-product-btn btn btn-danger" data-id="${productId}">
                    <i class="bi bi-trash"></i> Удалить
                </button>
            </td>
        `);
    });

    // 3. Удаление продукта
    $(document).on('click', '.delete-product-btn', function() {
        if (!confirm('Вы уверены, что хотите удалить этот продукт?')) {
            return;
        }

        const productId = $(this).data('id');
        const $row = $(this).closest('tr');

        $.ajax({
            url: `/products/delete/${productId}/`,
            type: "DELETE",
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function() {
                $row.remove();
                // Можно показать toast-уведомление об успешном удалении
            },
            error: function(response) {
                alert(response.responseJSON.error || 'Ошибка при удалении продукта');
            }
        });
    });
});

function saveProductChanges($row, productId) {
    const name = $row.find('.edit-name').val();
    const totalPrice = $row.find('.edit-price').val();
    const totalQuantity = $row.find('.edit-quantity').val();
    const unitId = $row.find('.edit-unit').val();

    $.ajax({
        url: `/products/update/${productId}/`,
        type: "POST",
        data: {
            'name': name,
            'total_price': totalPrice,
            'total_quantity': totalQuantity,
            'unit': unitId,
            'csrfmiddlewaretoken': getCookie('csrftoken')
        },
        success: function(response) {
            // Обновляем строку и data-атрибуты
            $row.data('name', response.name)
               .data('price', response.total_price)
               .data('quantity', response.total_quantity)
               .data('unit-id', response.unit_id)
               .data('unit-name', response.unit);


            $row.html(`
                <td>${response.name}</td>
                <td>${parseFloat(response.total_price).toFixed(2)}</td>
                <td>${parseFloat(response.total_quantity).toFixed(2)}</td>
                <td>${response.unit}</td>
                <td>
                    <button class="edit-product-btn btn btn-success" data-id="${productId}">
                        <i class="bi bi-pencil"></i> Изменить
                    </button>
                    <button class="delete-product-btn btn btn-danger" data-id="${productId}">
                        <i class="bi bi-trash"></i> Удалить
                    </button>
                </td>
            `);
        },
        error: function(response) {
            showErrors(response.responseJSON.error);
        }
    });
}

function showErrors(errors) {
    $('[data-bs-toggle="popover"]').popover('dispose');

    for (const field in errors) {
        const input = $(`#id_${field}`);
        const errorText = errors[field].join(', ');

        input.popover({
            trigger: 'manual',
            placement: 'top',
            content: errorText,
            container: 'body',
            template: `
                <div class="popover popover-error" role="tooltip">
                    <div class="popover-arrow"></div>
                    <div class="popover-header bg-danger text-white">Ошибка</div>
                    <div class="popover-body">${errorText}</div>
                </div>
            `
        });

        input.popover('show');

        // Автоматическое скрытие через 5 секунд
        setTimeout(() => input.popover('hide'), 5000);
    }
}
