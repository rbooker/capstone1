$("#quiz-select").change(function() {
    var quiz_id = $("#quiz-select option:selected").val();
    var quiz_rounds = $(`#quiz-${quiz_id}`).data("rounds")
    console.log(quiz_rounds)
    $("#round-select").empty()
    for (var i = 1; i <= quiz_rounds; i++){
        $("#round-select").append(
            $("<option>")
            .val(`${i}`)
            .text(`${i}`)
        );
    }
});

$("document").ready(function() {
    var quiz_id = $("#quiz-select option:selected").val();
    var quiz_rounds = $(`#quiz-${quiz_id}`).data("rounds")
    console.log(quiz_rounds)
    $("#round-select").empty()
    for (var i = 1; i <= quiz_rounds; i++){
        $("#round-select").append(
            $("<option>")
            .val(`${i}`)
            .text(`${i}`)
        );
    }
});