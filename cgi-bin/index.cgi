#!/usr/bin/perl
use strict;
use warnings;
use CGI;
use DBI;
use Date::Manip;
use JSON;
use HTML::Entities; #used to validate input


my $q = CGI->new();

# MySQL database configuration
my $dsn = "DBI:mysql:database=appointments";
my $username = "perl";
my $password = "perl";   
 
my $dbh  = DBI->connect($dsn,$username,$password);

my $date = $q->param('date');
my $time = $q->param('time');
my $datetime;
my $description = $q->param('description');
$description = HTML::Entities::encode($description); # used to prevent XSS
my $search = $q->param('search');


#print header before anything
print qq(Content-type: text/html\n\n);
print "$datetime";
#set html template
my $html = << "EndHTML";
<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8">
		 <base href="../">
		<link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
		<link rel="stylesheet" href="./css/stylesheet.css">
		<link rel="icon" type="image/x-icon" href="../favicon.ico">
		<title>Appointments</title>
	</head>
	<body>
		<div class="content">
			<div id="formError" class="error_desc">%s</div>
			<div id="newFormDiv">
				<span id="new" class="button green" title="Add new appointment">
					New
				</span>
				<span id="cancel" class="button red init-hide" title="Cancel new appointment">
					Cancel
				</span>
				<form id="newForm" name="newForm" class="init-hide" method="POST" action="./cgi-bin/index.cgi">
					<input id="datetime" type='hidden' name="datetime" />
					<div class="line">
						<span class="label">
							Date
						</span>
						<input id="date" name="date" type="text" readonly="readonly" />
					</div>
					
					<div class="line">
						<span class="label">
							Time
						</span>
						<input id="time" name="time" type="text" readonly="readonly" />
					</div>
					<div class="line">
						<span class="label">
							Description
						</span>
						<textarea id="description" name="description"></textarea>
					</div>
				</form>
			</div>
			<div class="line sep">
				<h3>Scheduled Appointments</h3>
			</div>
			<div class="search-div">
				<input id="search" type="text" placeholder="Search Appointments" />
				<span id="searchSub" class="green button" title="Search scheduled appointments">
					Search
				</span>
			</div>

			<div id="apt-div">
			</div>
		</div>
		
	</body>
		<link rel="stylesheet" type="text/css" href="./css/jquery.datetimepicker.css"/ >
		<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
		<script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
		<script src="./js/jquery.validate.js"></script>
		<script src="./js/jquery.datetimepicker.full.min.js"></script>
		<script src="./js/index.js"></script>
</html>
EndHTML

# function to determine if param is defined and not empty
sub isset {
	my ($var) = @_;
	return (defined $var && length $var > 0);
}

if(isset($date) && isset($time)) {
	$datetime = "$date $time";
}

# check if only one of the required fields is set
# set error and exit if only one parm is present
if(isset($datetime) xor isset($description)) {
	print sprintf($html, "All fields are required");
	exit;
}
elsif(isset($datetime) && isset($description)) {
	my $error = "";
	my $sql;
	my $stmt;

	# check if SQL table exists
	$sql = "SELECT * 
			FROM information_schema.tables
			WHERE table_schema = 'appointments' 
			    AND table_name = 'appointments'
			LIMIT 1;";
	$stmt = $dbh->prepare($sql);
	$stmt->execute();
	my $count = 0;
	while(my @row = $stmt->fetchrow_array()) {
	     $count++;
	  }  

	$stmt->finish();
	# create table if it doesn't exist
	if(!$count) {
		$sql = "CREATE TABLE `appointments`.`appointments` 
		( `id` INT NOT NULL AUTO_INCREMENT , `datetime` VARCHAR(20) NOT NULL ,
		 `description` TEXT NOT NULL ,
		  PRIMARY KEY (`id`)) ENGINE = InnoDB;";

		$stmt = $dbh->prepare($sql);
		$stmt->execute();
	}

	# validate inputs
	# already checked if description is there
	# only need to check datetime
	if($datetime = ParseDate($datetime)) {
		# pass
	}
	else {
		$error = "Invalid datetime";
	}
	

    # insert into table if valid
    if($error == "") {
	    $sql = "INSERT INTO appointments(datetime,description)
	    VALUES(?,?)";
	    $stmt = $dbh->prepare($sql);
	    if(!$stmt->execute($datetime,$description)) {
	    	$error = DBI::errstr;
	    	
	    }
	}

    print sprintf($html, $error);
    exit;
    

}

# render front end if search isn't set
if(!defined $search) {
	print sprintf($html, "");
	exit;
}
else {
	my $sql;
	my $stmt;
	$sql = "SELECT * 
			FROM appointments
			WHERE description LIKE ?
			ORDER BY datetime;";

	$stmt = $dbh->prepare($sql);
	$stmt->execute('%'.$search.'%');
	my @result;
	
	my $count = 0;
	while (my $ref = $stmt->fetchrow_hashref()) {
		  my %thisRow;
		  while ((my $key, my $value) = each(%$ref)) {
		  	  $thisRow{$key}=$value;
		  }
		  push(@result,  \%thisRow);
		  $count++;
      }
 


	$stmt->finish();
	#print qq(Content-type: text/json\n\n);
	print encode_json \@result;
		
}


$dbh->disconnect();
