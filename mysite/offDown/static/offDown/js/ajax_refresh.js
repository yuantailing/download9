'use strict';
function refresh() {
    $("[name$='statusTable']").each(function () {
        var id = $(this).attr("id");
        
        var url = "gets/?id=" + id.toString();
        
        var thisTable = $(this);
        console.log(thisTable);
        $.get(url, function(data, status){
            var x = JSON.parse(data);
            console.log(thisTable);
            thisTable.children("[name='status']").text(x.taskStatus);
            thisTable.children("[name='rate']").text(x.taskRate+"%");
            thisTable.children("[name='speed']").text(x.taskSpeed+"KiB");
        });
        ;
    });
}
setInterval("refresh()",5000); 