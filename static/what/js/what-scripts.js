$(document).ready(function() {
	function pad(num) {
		if (num < 10)
			return "0" + num;
		else
			return num + "";
	}

	function load_student(id) {
		$.ajax({
			type: "GET",
			dataType: "json",
			url: id.toString() + "/quizzes/",
			success: function(data) {
				var dialog_content = "<table border='0' width='100%'>";
				dialog_content += "<tr><td width='50%'>Name:</td>";
				dialog_content += "<td>" + data.annal + "</td></tr>";
				dialog_content += "<tr><td width='50%'>Submitted:</td>";
				dialog_content += "<td>" + (data.submitted).toString() + "</td></tr>";
				dialog_content += "<tr><td width='50%'>Score:</td>";
				dialog_content += "<td>" + (data.score).toString() + "</td></tr>";
				dialog_content += "<tr><td width='50%'>Number of questions:</td>";
				dialog_content += "<td>" + (data.number_of_questions).toString() + "</td></tr>";
				dialog_content += "<tr><td width='50%'>Start time:</td>";
				dialog_content += "<td>" + (data.start_time).toString() + "</td></tr>";
				dialog_content += "<tr><td width='50%'>Finished in:</td>";
				dialog_content += "<td>" + (data.finish_time).toString() + "</td></tr>";
				dialog_content += "</table>";
				return dialog_content;
			},
		});
	}

	$('.selectpicker').selectpicker();

	$("#select-locale").change(function() {
		$("#locale-hidden").val($("#select-locale").find("option:selected").val());
		$("#form-change-locale").submit();
	});

	$("#navbar-rules").click(function() {
		var rules = $("#rules-hidden").attr("value") || "No rules.";
		var rules_title = $("#rules-title-hidden").attr("value");
		var dialog_close = $("#close-hidden").attr("value");
		bootbox.dialog({
			title: rules_title,
			message: rules,
			buttons: {
				main: {
					label: dialog_close,
					className: "btn-primary"
				}
			}
		});
	});

	$(".student-nb-quizzes").click(function() {
		var dialog_previous = $("#previous-hidden").attr("value");
		var dialog_next = $("#next-hidden").attr("value");
		var dialog_close = $("#close-hidden").attr("value");
		var dialog_title = $(this).attr("tag2");
		var current_id = $(this).attr("tag");
		var previous_id = $(this).attr("tag-previous");
		var next_id = $(this).attr("tag-next");
		$.ajax({
			type: "GET",
			dataType: "json",
			url: current_id + "/quizzes/",
			success: function(data) {
				// var dialog_content = "<table border='0' width='100%'>";
				// dialog_content += "<tr><td width='50%'>Name:</td>";
				// dialog_content += "<td>" + data.annal + "</td></tr>";
				// dialog_content += "<tr><td width='50%'>Submitted:</td>";
				// dialog_content += "<td>" + (data.submitted).toString() + "</td></tr>";
				// dialog_content += "<tr><td width='50%'>Score:</td>";
				// dialog_content += "<td>" + (data.score).toString() + "</td></tr>";
				// dialog_content += "<tr><td width='50%'>Number of questions:</td>";
				// dialog_content += "<td>" + (data.number_of_questions).toString() + "</td></tr>";
				// dialog_content += "<tr><td width='50%'>Start time:</td>";
				// dialog_content += "<td>" + (data.start_time).toString() + "</td></tr>";
				// dialog_content += "<tr><td width='50%'>Finished in:</td>";
				// dialog_content += "<td>" + (data.finish_time).toString() + "</td></tr>";
				// dialog_content += "</table>";
				var dialog_content = load_student(current_id);
				bootbox.dialog({
					title: dialog_title,
					message: dialog_content,
					buttons: {
						previous: {
							label: dialog_previous,
							className: "btn-success",
							callback: load_student(previous_id)
						},
						next: {
							label: dialog_previous,
							className: "btn-success",
							callback: load_student(next_id)
						},
						close: {
							label: dialog_close,
							className: "btn-primary"
						}
					}
				});
			},
		});
	});

	$("#delete-selected").click(function() {
		var confirm_yes = $("#confirm-yes").attr("value");
		var confirm_no = $("#confirm-no").attr("value");
		var confirm_title = $("#confirm-title").attr("value");
		var confirm_message = $("#confirm-message").attr("value");
		bootbox.dialog({
			title: confirm_title,
			message: confirm_message,
			buttons: {
				yes: {
					label: confirm_yes,
					className: "btn-danger",
					callback: function () {
						$("#changelist-action").val("delete");
						$("#changelist-form").submit();
					}
				},
				no: {
					label: confirm_no,
					className: "btn-primary"
				}
			}
		});
	});

	$(".answers").click(function() {
		if ($(this).hasClass("yellow")) {
			$(this).removeClass("yellow");
			$(this).parent().find(".chosen-answer").val("");
		} 
		else {
			var question_id = ($(this).parent().attr("id")).substring(8);
			var answer_id = ($(this).attr("id")).substring(6);
			$(".answer-q" + question_id).removeClass("yellow");
			$(this).addClass("yellow");
			$(this).parent().find(".chosen-answer").val(answer_id);
		}		
	});

	$("#submit-button").click(function() {
		$("#form-submit").submit();
	});

	$("#login-success-alert").fadeIn();
	$("#login-success-alert").delay(3000).fadeOut();

	$("#sel-toggle-all").change(function() {
		if (this.checked)
			$(".sel-item").prop("checked", true);
		else
			$(".sel-item").prop("checked", false);
	});

	var timer = setInterval(function() {
		var ending_soon = false;
		var remaining_time = parseInt($("#remaining-time-hidden").attr("value"));
		if (remaining_time <= 0) {
			clearInterval(timer);
			$("#form-submit").submit();
		}
		else {
			var display_time = "";
			var hours;
			var minutes;
			var seconds;
			remaining_time--;
			if (remaining_time <= 30)
				ending_soon = true;
			else
				ending_soon = false;
			if (ending_soon) {
				$(".circle").css("background", "linear-gradient(135deg, #f85032 0%,#f16f5c 50%,#f6290c 51%,#f02f17 71%,#e73827 100%)");
				$(".circle-border").css("border", "3px solid #882222");
			}
			if (remaining_time < 60) {
				seconds = remaining_time.toString();
				display_time = seconds;
			}
			else if (remaining_time < 3600) {
				minutes = Math.floor(remaining_time / 60);
				seconds = remaining_time % 60;
				display_time = pad(minutes) + ":" + pad(seconds);
			}
			else {
				hours = Math.floor(remaining_time / 3600);
				minutes = Math.floor((remaining_time - hours * 3600) / 60);
				seconds = remaining_time % 60;
				display_time = hours + ":" + pad(minutes) + ":" + pad(seconds);
			}
			$("#remaining-time-hidden").val(remaining_time.toString());
			$(".time-text").text(display_time);
		}
	}, 1000);
});
