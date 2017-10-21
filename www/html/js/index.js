$(document).ready(function(){

	// init datepicker
	$("#date").datetimepicker({
		minDate:0,
		roundTime: 'round',
		timepicker: false,
		format:'m/d/Y',
  		
	});

	// init timepicker
	$("#time").datetimepicker({
		datepicker: false,
		format: 'h:i A',
		formatTime: 'h:i a',
		step: 10

	});

	/* DATETIME PICKER HAS A BUG THAT REDUCES THE TIME BY ONE
	HOUR ON BLUR, THIS IS TO FIX THAT*/

	$('#time').blur(function(){
		var time = $(this).val();
		if(time != '') {
			time = time.split(':');
			var hour = parseInt(time[0]);
			if(hour == 12) {
				hour = 1;
			}
			else {
				hour++;
			}
			hour = hour.toString();
			if(hour.length != 2) {
				hour = "0"+hour;
			}
			time[0] = hour;
			time = time.join(':');
		}
		$(this).val(time);
	})

	/* END BUG FIX */


	// validation parameters
	$('#newForm').validate({ 
	    rules: { 
	        date: { 
	            required: true
	        },
	        time: {
	        	required: true
	        },
	        description: {
	        	required: true
	        }

	    },

	    messages:{
	    	date: {
	    		required: "Date is required"
	    	},
	    	time: {
	    		required: "Time is required"
	    	},

	    	description: {
	    		required: "Description is required"
	    	}
	    },

	    // place error message in custom error div
	    errorPlacement: function (error, element) {
	    	$("#formError").html('');
            error.appendTo($("#formError"));
        }  
	});

	// parse datetime and format into h:i a
	function formatTime(datetime) {
		var time = datetime.substr(8);
		time = time.split(':');
		var hour = parseInt(time[0]);
		var minute = time[1];
		var merid = 'am';

		if(hour === 0) {
			hour = 12;
		}
		else if(hour > 12) {
			hour -= 12;
			merid = 'pm';
		}

		return hour.toString()+":"+minute+merid;
	}

	// object to translate numbers to months
	var int2month = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",
	7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"};

	// parse datetime and format into M d
	function formatDate(datetime) {
		var date = datetime.substr(0,8);
		var year = date.substr(0,4);
		var month = date.substr(4,2);
		var day = date.substr(6,2);

		var formattedMonth = int2month[parseInt(month)];

		return formattedMonth + " " + day;
	}

	// function to new rows for appointment table
	function makeRow(datetime,description) {
		return "<tr><td>"+formatDate(datetime)+"</td><td>"+formatTime(datetime)+"</td><td>"+description+"</td></tr>";
	}

	/* function takes a search term as an argument
	conducts AJAX call to index.cgi
	expects JSON as a return
	parses JSON and formats rows into table */
	function getAppointments(q) {
		$('#apt-div').html('Loading...');
		var url = "./cgi-bin/index.cgi";
		var data = {search:q};

		$.ajax({
			url: url,
			method: 'POST',
			data: data,
			dataType: 'json',
			success: function(data, status) {
				var table = "<table>";
				

				if (data.length > 0) {
					table += "<tr><th>Date</th><th>Time</th><th>Description</th></tr>";
					$.each(data, function() {
						table += makeRow(this.datetime,this.description);
					})

				}
				else {
					table += "<tr><td><i>No Appointments</i></td></tr>"
				}

				table += "</table>"

				

				$('#apt-div').html(table);
			}
		})
	}

	// initialize appointment table
	// send empty string to get all results from SQL table
	getAppointments('');

	//bind search button
	$('#searchSub').click(function(){
		var q = $('#search').val();
		getAppointments(q);
	})

	// bind pressing enter key in search field
	$('#search').keypress(function(e) {
		if(e.which == 13) {
			$('#searchSub').click();
		}
	})

	// resets new appointment form
	function resetForm() {
		$('.init-hide').hide();
		$('#formError').html('');
		$('#date').val('');
		$('#time').val('');
		$('#description').val('');
	}

	// Show form when #new is clicked
	$('body').on('click', '#new', function() {
		$('.init-hide').show();
		$('#new').text('Add');

		// Change function to submit
		$('#new').off('click');
		$('#new').click(function() {
			$('#newForm').submit();
			$('.init-hide').hide();
			// restore new button
			$('#new').text('New');
		})

		$("#cancel").click(function () {
			$('#new').off('click');
			resetForm();
			// restore new button
			$('#new').text('New');
		})



	})


})