function unique(a) {
    var temp = {};
    for (var i = 0; i < a.length; i++)
        temp[a[i]] = true;
    var r = [];
    for (var k in temp)
        r.push(k);
    return r;
}


function ajax_call(type, url, data, callback_function) {
    $.ajax({
        type: type,
        url: url,
        data: JSON.stringify(data),
        dataType: 'json',
        contentType: 'application/json; charset=UTF-8',
        error: function( jqXHR, textStatus, errorThrown ){
            $('#notificationarea').html("jsoncall failed! reason:" + textStatus +", " + errorThrown);
        },
        success: callback_function
    });
}


function buildTableParameters(columnwidths, addparams) {
    var parameters =  { 
        "bJQueryUI": true,
        "bProcessing": true,
        "sPaginationType": "full_numbers",
        //"aaSorting": [[ 0, "asc" ]],
        "aLengthMenu": [[25, 50, 75, -1], [25, 50, 75, "All"]],
        "iDisplayLength": -1
        //"aoColumnDefs": [
        //    { "bVisible": false, "aTargets": [0] }, //set column visibility            
        //    {"sType": "numeric", "aTargets": [0] }, //define data type for specified columns
        //    {"iDataSort": 0, "aTargets": [1] } //sort based on a hidden column when another column is clicked            
        //]
    }; 
    var columns = [];
    for (var i=0; i < columnwidths.length; i++) {
        columns.push({ 'width':  columnwidths[i].toString() + "px" })
    }
    parameters.columns = columns;
    for (var key in addparams) {
        parameters[key] = addparams[key];
    }
    return parameters
}


function dot2num(dot) 
{
    var d = dot.split('.');
    return ((((((+d[0])*256)+(+d[1]))*256)+(+d[2]))*256)+(+d[3]);
}


function num2dot(num) 
{
    var d = num%256;
    for (var i = 3; i > 0; i--) { 
        num = Math.floor(num/256);
        d = num%256 + '.' + d;
    }
    return d;
}