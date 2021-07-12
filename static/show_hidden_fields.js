$("#round-select").change(function() {
    var rounds = $("#round-select option:selected").val();
    console.log(`${rounds}`);
    for (var i = 1; i <= 5; i++){
        if(i <= rounds)
            $(`#diff-round${i}`).show();
        else
            $(`#diff-round${i}`).hide();
    }
});

$("document").ready(function() {
    var rounds = $("#round-select option:selected").val();
    console.log(`${rounds}`);
    for (var i = 1; i <= 5; i++){
        if(i <= rounds)
            $(`#diff-round${i}`).show();
        else
            $(`#diff-round${i}`).hide();
    }
});