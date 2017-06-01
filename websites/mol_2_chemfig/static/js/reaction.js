$( document ).ready(function() {

    $('#chemfig').hide();
    var text_above_arrow = [];
    var text_bellow_arrow = [];
    var chemfig_code = "";
    var constant_chemfig = "";
    $("input[value='-w']").prop('checked', true);

    var hide_elements = ["#sketcher2_button_scale_plus", "#sketcher2_button_scale_minus",
			 "#sketcher2_button_open", "#sketcher2_button_save",
			 "#sketcher2_buttons_attribute"];

    $.each(hide_elements, function(index, value){
	$(value).hide();
    });

    // Set id for sketcher toolbar
    $('div[style="font-size:10px;"]').attr('id', 'sketcher_toolbar');

    // Add text input
    $('#sketcher_toolbar').append($("<input>", {id: "arrow_text", type: "text",
    						class: "w3-round",
    						placeholder: "text above arrow; text below arrow"}));
    // Add text button
    $('#sketcher_toolbar').append($("<input/>", {id: "add_text",
    						 type: "button",
    						 class:"w3-btn w3-ripple w3-teal w3-tiny w3-round",
    						 value: "Add"}));
    // Create Clear text button
    $('#sketcher_toolbar').append($("<input/>", {id: "remove_text",
    						 type: "button",
    						 class:"w3-btn w3-ripple w3-red w3-tiny w3-round",
    						 value: "Clear"}));

    function get_options(){
	var chbx=[];		
	$('input[name="check"]:checked').each(function () {
	    chbx.push(this.value);
	});
	return chbx;
    }

    function convert(el, options, remove_class = true){
	var molecules = sketcher2.molecules;
        var shapes = sketcher2.shapes;
	var reaction = JSON.stringify(new ChemDoodle.io.JSONInterpreter().contentTo(molecules, shapes));
	var input_text = $("#arrow_text").val();
        //alert JSON.stringify($('sketcher_canvas').children()));
	// alert(reaction);
        var num_of_molecules = Object.keys(molecules).length;
        var MOLFiles = [];
        for(var i = 0; i < num_of_molecules; i ++){
            var molFile = ChemDoodle.writeMOL(molecules[i]);
            MOLFiles.push(molFile);
        };
	$.ajax({
            type: "POST",
            url: "/mol_2_chemfig/convert_reaction",
            contentType: 'application/json; charset=UTF-8',
            data: JSON.stringify({'MOLFiles': MOLFiles,
                                  'reaction': reaction,
				  'input_text': input_text,
				  'options': options}),
            dataType: 'json',
            success: function(data){
                $('#reaction').val(data.data);
		chemfig_code = data.data;
		constant_chemfig = data.data;
                $("#pdf").attr('src', data.pdflink);
		if(remove_class){
		    $(el).removeClass("w3-disabled");
		}
            },
            error: function(error){
                console.log(error);
            },
        });
    }
    
    $('#convert2').on('click', function(){
	$("#convert2").addClass("w3-disabled");
	$('input[name="check"]').attr('checked', false);
	$( "input[value='-w']" ).prop('checked', true);
	convert("#convert2", get_options());
	$('#chemfig').show();
    });



    // $(document).keyup(function (e) {
    // 	if ($("#to_chemfig:focus")) {
    // 	    var input = $('#to_chemfig').val();
    // 	    var numbers = '0123456789';
    //         var brackets = '()';
    //         var percent = '%';
    //         var length = input.length;
    //         var output = '';
    // 	    if ($('#celcius').is(':checked')) {
    // 		for (i = 0; i < length; i++) {
    //                 var current = input[i]
    //                 if (current === "C"){
    //                     var new_char = current.replace(current, "$^\\circ$"+current);
    //                     output += new_char;
    //                 }
    //                 else {
    //                     output += current;
    //                 }
    //             }
    // 		$("#output").text(output);
    // 	    }
    // 	    else {
    //             for (i = 0; i < length; i++) {
    //                 var current = input[i]
    //                 if (numbers.indexOf(current) != -1){
    //                     var new_char = current.replace(current, "$_"+current+"$");
    //                     output += new_char;
    //                 }
    //                 else if(brackets.indexOf(current) != -1){
    //                     var new_char = current.replace(current, "{"+current+"}");
    //                     output += new_char;
    //                 }
    //                 else if(percent.indexOf(current) != -1){
    //                     var new_char = current.replace(current, "\\"+current);
    //                     output += new_char;
    //                 }
    //                 else {
    //                     output += current;
    //                 }
    //             }
    // 		$("#output").text(output);
    //         }
 
    	//}
    //});

    $('#add_text').on('click', function(){
	var input_text = $('#arrow_text').val();
	var shapes = sketcher2.shapes;
	var molecules = sketcher2.molecules;
	var num_of_arrows = shapes.length;
	if(input_text == ''){
	    alert("Please enter reaction conditions!");
	}
	else if (num_of_arrows == 0){
	    alert("Your reaction must have at least 1 arrow")
	}
	else{
	    // alert(JSON.stringify(new ChemDoodle.io.JSONInterpreter().contentTo(molecules,shapes)));
	    // alert(JSON.stringify(shapes));
	    $.ajax({
		type: "POST",
		url: "/mol_2_chemfig/parse_input_text",
		contentType: 'application/json; charset=UTF-8',
		data: JSON.stringify({'input_text': input_text}),
		dataType: 'json',
		success: function(data){
		    for(var i = 0; i < data.splitted_text.length; i++){
			try {
			shapes[i].topText = data.splitted_text[i][0];
			shapes[i].bottomText = data.splitted_text[i][1];
			}
			catch(error) {}
		    sketcher2.loadContent(molecules, shapes);
		    }                    
		},
		error: function(error){
                    // console.log(error);
		},
            });
	}	
    })

    $('#remove_text').on('click', function(){
	$('#arrow_text').val("");
	var shapes = sketcher2.shapes;
	var molecules = sketcher2.molecules;
	var num_of_arrows = shapes.length;
	for(var i = 0; i < num_of_arrows; i++){
	    shapes[i].topText = '';
	    shapes[i].bottomText = '';
        }
        sketcher2.loadContent(molecules, shapes);
    })

    function inline(text){
	// text = $('#reaction').val();
	$.ajax({
	    type: "POST",
	    url: "/mol_2_chemfig/get_inline",
	    contentType: 'application/json; charset=UTF-8',
	    data: JSON.stringify({"text": text}),
	    dataType: 'json',
	    success: function(data){
		$('#reaction').val(data.chemfig);
	    },
	    error: function(error){
		console.log(error);
	    }
	}); 
    };

    function remove_percent(){
	text = $('#reaction').val();
	$.ajax({
	    type: "POST",
	    url: "/mol_2_chemfig/remove_after_percent",
	    contentType: 'application/json; charset=UTF-8',
	    data: JSON.stringify({"text": text}),
	    dataType: 'json',
	    success: function(data){
		$('#reaction').val(data.chemfig);
	    },
	    error: function(error){
		console.log(error);
	    }
	}); 
    };

    $("#apply").on('click', function(){	
	var chbx = get_options();
	// if(chbx.indexOf('-rm') != -1 & chbx.indexOf('-j') != -1 ){
	//     var warning = '<strong>Please select either "inline" or "remove %" checkbox but not both.<strong>';
	//     $('#warning').html(warning);
	//     $('#not_found').css('display', 'block');
	// }
	// else if(chbx.indexOf('-w') != -1 & chbx.indexOf('-rm') != -1){
	//     remove_percent();
	// }
	if(chbx.length == 2 & chbx.indexOf('-w') != -1 & chbx.indexOf('-j') != -1){
	    inline(chemfig_code);
	}
	else if(chbx.length > 2 & chbx.indexOf('-j') != -1){
	    $("#apply").addClass("w3-disabled");
	    chbx.splice( $.inArray('-j', chbx), 1);
	    $("#apply").addClass("w3-disabled");
	    convert("#apply", chbx);
	    inline(chemfig_code);
	}
	else {
	    $("#apply").addClass("w3-disabled");
	    convert("#apply", chbx);
	}
    })

    function reset_options(){
	$('input[name="check"]').attr('checked', false);
	$( "input[value='-w']" ).prop('checked', true);
    }
    
    $('#reset').on('click', function(){
	var chbx = get_options();
	if(chbx.length == 2 & chbx.indexOf('-j') != -1 & chbx.indexOf('-w') != -1){
	    $('#reaction').val(constant_chemfig);
	    reset_options();
	}
	else if (chbx.length > 2 & chbx.indexOf('-j') != -1){
	    $("#reset").addClass("w3-disabled");
	    reset_options();
	    // chbx.splice( $.inArray('-j', chbx), 1);
	    convert("#reset", ['-w']);
	}
	else if (chbx.indexOf('-j') == -1){
	    $("#reset").addClass("w3-disabled");
	    // alert(chbx);
	    convert("#reset", ['-w']);	    
	    reset_options();
	}
	
    })

    $('#chemfig').on('click', function(){
	text = $('#reaction').val();
	$("#chemfig").addClass("w3-disabled");
	$.ajax({
	    type: "POST",
	    url: "/mol_2_chemfig/change_chemfig",
	    contentType: 'application/json; charset=UTF-8',
	    data: JSON.stringify({"text": text}),
	    dataType: 'json',
	    success: function(data){
		$("#pdf").attr('src', data.pdflink);
		$('#chemfig').removeClass("w3-disabled")
	    },
	    error: function(error){
		console.log(error);
	    }
	}); 
    })
 });
