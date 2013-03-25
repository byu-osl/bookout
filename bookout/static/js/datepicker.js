$(function(){
	$(".datepicker").datepicker().on('changeDate', function(){
		$(this).datepicker('hide');
	});
})