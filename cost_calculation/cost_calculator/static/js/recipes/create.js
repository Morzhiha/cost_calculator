$(document).ready(function() {
    const productsData = JSON.parse($('#products-data').text());
    const productsMap = {};

    $.each(productsData, function(i, product) {
        productsMap[product.id] = {
            unit: product.unit__short_name,
            price: parseFloat(product.price_per_base_unit)
        };
    });

    const editMode = JSON.parse($('#edit-mode').text());
    const recipeId = JSON.parse($('#recipe-id').text());

    const formUrl = editMode ? `/recipes/${recipeId}/` : '/recipes/create/';


    function hasUnsavedChanges() {
        let hasChanges = false;
        $('.ingredient-row').each(function() {
            const $row = $(this);
            if ($row.find('select').val() || $row.find('input[type="number"]').val()) {
                hasChanges = true;
                return false;
            }
        });
        return hasChanges;
    }
    $(document).on('click', '#add-products-link', function(e) {
        e.preventDefault();
        const redirectUrl = $(this).attr('href');

        if (hasUnsavedChanges()) {

            if (confirm('У вас есть несохраненные изменения. Хотите сохранить рецепт перед переходом?')) {
                $('#recipe-form').one('submit', function() {
                    window.location.href = redirectUrl;
                }).submit();
            } else {
                window.location.href = redirectUrl;
            }
        } else {
            window.location.href = redirectUrl;
        }
    });

    function updateForms() {
        const totalForms = $('#ingredients-list tr').length;
        $('#id_ingredients-TOTAL_FORMS').val(totalForms);

        $('#ingredients-list tr').each(function(i) {
            $(this).find(':input').each(function() {
                const name = $(this).attr('name');
                if (name) {
                    const newName = name.replace(/-\d+-/, '-' + i + '-');
                    $(this).attr('name', newName);
                    $(this).attr('id', 'id_' + newName);
                }
            });
        });
        updatePrices();
        updateProductOptions();
    }

    function updateProductOptions() {
        const usedValues = [];
        $('.ingredient-row select').each(function() {
            const val = $(this).val();
            if (val) usedValues.push(val);

            const quantityInput = $(this).closest('tr').find('.quantity-input');
            quantityInput.prop('disabled', !val);
            if (!val) quantityInput.val('');
        });

        $('.ingredient-row select').each(function() {
            const currentSelect = $(this);
            const currentValue = currentSelect.val();

            currentSelect.find('option').each(function() {
                const option = $(this);
                const optionValue = option.val();

                option.prop('disabled', false);
                option.prop('hidden', false);

                if (optionValue && optionValue !== currentValue && usedValues.includes(optionValue)) {
                    option.prop('disabled', true);
                    option.prop('hidden', true);
                }
            });
        });
        const availableProducts = Object.keys(productsMap).filter(id => !usedValues.includes(id));
        const noIngredients = availableProducts.length === 0 && Object.keys(productsMap).length > 0;

        $('#no-ingredients-alert').toggleClass('d-none', !noIngredients);
    }

    function updatePrices() {
        let totalCost = 0;

        $('.ingredient-row').each(function() {
            const $row = $(this);
            const productId = $row.find('.product-select').val()
            const quantity = parseFloat($row.find('.quantity-input').val()) || 0;

            if (productId && productsMap[productId]) {
                const product = productsMap[productId];
                const cost = product.price * quantity;

                $row.find('.unit-short').text(product.unit);
                $row.find('.unit-price').text(product.price.toFixed(2));
                $row.find('.ingredient-cost').text(cost.toFixed(2));
                totalCost += cost;
            } else {
                $row.find('.unit-short, .unit-price').text('-');
                $row.find('.ingredient-cost').text('0.00');
            }
        });

        $('#total-cost').text(totalCost.toFixed(2));
        const totalWeight = parseFloat($('#id_weight').val()) || 0;
        const neededWeight = parseFloat($('#id_need_weight').val()) || 100;

        const costForWeight = totalWeight > 0 ? (totalCost / totalWeight) * neededWeight : 0;

        $('#cost-per-weight').text(costForWeight.toFixed(2));
        $('#weight-display').text(neededWeight);
    }


    function addNewIngredientRow() {
        const lastRow = $('#ingredients-list tr:last');

        const newRow = lastRow.clone();

        newRow.find('select').val('');
        newRow.find('input').val('').prop('disabled', true);
        newRow.find('.unit-price').text('-');
        newRow.find('.ingredient-cost').text('0.00');
        // newRow.find('.remove-row').prop('disabled', true);

        lastRow.find('.remove-row').prop('disabled', false).css('visibility', 'visible');

        $('#ingredients-list').append(newRow);
        updateForms();
    }

    $(document)
        .on('change', '.product-select', function (){
            const $row = $(this).closest('tr');
            const isLastRow = $row.is(':last-child');

            if (isLastRow && $(this).val()) {
                addNewIngredientRow();
            }
            updateProductOptions();
            updatePrices();
        })
        .on('input', '.quantity-input', updatePrices)
        .on('input', '#id_weight, #id_need_weight', updatePrices)
        .on('click', '.remove-row', function() {
        if ($('.ingredient-row').length > 1) {
            $(this).closest('tr').remove();
            updateForms();
        } else {
            alert('Должен остаться хотя бы один ингредиент!');
        }
    });

    updateForms();

    $('#recipe-form').submit(function(e) {
        e.preventDefault();

        const formData = new FormData(this);

        $('.ingredient-row').each(function(index) {
            const product = $(this).find('.product-select').val();
            const quantity = $(this).find('.quantity-input').val();
            if (product && quantity) {
                formData.append(`ingredients-${index}-product`, product);
                formData.append(`ingredients-${index}-quantity`, quantity);
            }
        });
        $.ajax({
            url: formUrl,
            method: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                alert('Рецепт добавлен');
                window.location.href = response.redirect;
            },
            error: function(xhr) {
                console.error(xhr.responseJSON.errors);
                alert('Ошибка при сохранении рецепта');
            }
        });
    });
});