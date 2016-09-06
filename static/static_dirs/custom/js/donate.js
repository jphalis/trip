'use strict';

$(document).ready(function() {
    // Toggle form submit content when clicked
    var submitButton = $('#submitButton');

    submitButton.on('click', function() {
        // disable the button to prevent multiple submissions
        submitButton.attr('disabled', 'disabled').addClass('btn-disabled');
        submitButton.parents('form:first').submit();
    });
});