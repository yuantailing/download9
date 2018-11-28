'use strict';
function refresh() {
    $("[name$='statusTable']").each(function () {
        var id = $(this).attr("id");
        
        var url = "gets/?id=" + id.toString();
        
        var thisTable = $(this);
        //console.log(thisTable);
        $.get(url, function(data, status){
            var x = JSON.parse(data);
            console.log(x.taskCompletedTime);
            thisTable.children("[name='status']").text(x.taskStatus);
            thisTable.children("[name='rate']").text(x.taskRate+"%");
            thisTable.children("[name='speed']").text(x.taskSpeed+"KiB/s");
            thisTable.children("[name='size']").text(x.taskFilesize+"MB");
            if(x.taskCompletedTime != "None")
            {
                thisTable.attr("class", "success");
                var downloadLink="<a href=\"/download9/static/download/" + x.realFilename + "\">下载</a>";
                thisTable.children("[name='file']").html(downloadLink);
            }
        });
        ;
    });
}
setInterval("refresh()",2000); 
