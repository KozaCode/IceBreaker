document.addEventListener('DOMContentLoaded', function() {
    //Keep min age lower than max age
    min_age_field = document.getElementById('min_age_pref');
    max_age_field = document.getElementById('max_age_pref');

    min_age_field.max = max_age_field.value;
    max_age_field.min = min_age_field.value;

    min_age_field.addEventListener('change', function() {
        max_age_field.min = min_age_field.value;
        if(min_age_field.value > max_age_field.value) {
            min_age_field.value = max_age_field.value;
        }
    });
    max_age_field.addEventListener('change', function() {
        min_age_field.max = max_age_field.value;
        if(max_age_field.value < min_age_field.value) {
            max_age_field.value = min_age_field.value;
        }
    });
});