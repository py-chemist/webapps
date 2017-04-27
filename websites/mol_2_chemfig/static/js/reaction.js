$( document ).ready(function() {

    var text_above_arrow = [];
    var text_bellow_arrow = [];
     $( "input[value='-w']" ).prop('checked', true);

    var hide_elements = ["#sketcher2_button_scale_plus", "#sketcher2_button_scale_minus",
			 "#sketcher2_button_open", "#sketcher2_button_save",
			 "#sketcher2_buttons_attribute"];

    $.each(hide_elements, function(index, value){
	$(value).hide();
    });

    // Set id for sketcher toolbar
    $('div[style="font-size:10px;"]').attr('id', 'sketcher_toolbar');
    $('#sketcher_toolbar').append($("<input>", {id: "arrow_text", type: "text",
    						class: "w3-round",
    					       placeholder: "text above arrow; text below arrow"}));
    $('#sketcher_toolbar').append($("<input/>", {id: "add_text",
    						 type: "button",
    						 class:"w3-btn w3-ripple w3-teal w3-tiny w3-round",
    						 value: "Add"}));
    $('#sketcher_toolbar').append($("<input/>", {id: "remove_text",
    						 type: "button",
    						 class:"w3-btn w3-ripple w3-red w3-tiny w3-round",
    						 value: "Clear"}));

    $('#convert2').on('click', function(){
	$("#convert2").addClass("w3-disabled");
	var molecules = sketcher2.molecules;
        var shapes = sketcher2.shapes;
	var reaction = JSON.stringify(new ChemDoodle.io.JSONInterpreter().contentTo(molecules, shapes));
	var input_text = $("#arrow_text").val();
        //alert(JSON.stringify($('sketcher_canvas').children()));
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
				  'input_text': input_text}),
            dataType: 'json',
            success: function(data){
                $('#reaction').val(data.data);
                $("#pdf").attr('src', data.pdflink);
		$("#convert2").removeClass("w3-disabled");
            },
            error: function(error){
                console.log(error);
            },
        });
    });



    // $(document).keyup(function (e) {
    // 	if ($("#arrow_text:focus") && (e.keyCode === 13)) {
    //         var input_text = $("#arrow_text").val();
    //         var molecules = sketcher2.molecules;
    //         var shapes = sketcher2.shapes;
    // 	    // alert(JSON.stringify(new ChemDoodle.io.JSONInterpreter().contentTo(molecules,shapes)));
    // 	    // alert(JSON.stringify(shapes));
    //         var num_of_arrows = shapes.length;
    //         var all_text = input_text.split('|');
    // 	    // alert(input_text);

    //         for(var i = 0; i < num_of_arrows; i++){
    // 		var arrow_text = all_text[i].split(";");
    //             shapes[i].topText = arrow_text[0];
    // 	        text_above_arrow.push(arrow_text[0]);
    //             shapes[i].bottomText = arrow_text[1];
    // 		text_bellow_arrow.push(arrow_text[1]);
    //         }
    //         sketcher2.loadContent(molecules, shapes);
    // 	}
    // });

    $('#add_text').on('click', function(){
	var input_text = $('#arrow_text').val();
	// alert(input_text);
	var shapes = sketcher2.shapes;
	var molecules = sketcher2.molecules;
	var num_of_arrows = shapes.length;
	if(input_text == ''){
	    alert("Please enter reaction conditions!");
	}
	else if (num_of_arrows == 0){
	    alert("Youe reaction must have at least 1 arrow")
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
			shapes[i].topText = data.splitted_text[i][0];
			shapes[i].bottomText = data.splitted_text[i][1];
		    sketcher2.loadContent(molecules, shapes);
		    }                    
		},
		error: function(error){
                    console.log(error);
		},
            });
            
            // var all_text = input_text.split('|');
	    // // alert(num_of_arrows);

            // for(var i = 0; i < num_of_arrows; i++){
	    // 	var arrow_text = all_text[i].split(";");
	    // 	shapes[i].topText = arrow_text[0];
	    // 	text_above_arrow.push(arrow_text[0]);
	    // 	shapes[i].bottomText = arrow_text[1];
	    // 	text_bellow_arrow.push(arrow_text[1]);
            // }
            // sketcher2.loadContent(molecules, shapes);
	    
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
});
