from django.shortcuts import render, redirect, get_object_or_404
from .models import Hall, Booking
from .forms import HallUpdateForm
from django.db.models import Q
from django.contrib import messages
from datetime import datetime
from django.core.mail import send_mail
from datetime import datetime
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.shortcuts import render
from .models import Hall, Booking

def check_availability(request):
    halls = []
    locations = ["Chennai", "Trichy", "Vizag", "Kadapa", "Trivandrum", "Bangalore", "Mysore", "Munnar", "Thanjavur", "Kancheepuram", "Amaravti", "Hyderabad", "Secunderabad"]
    location = None
    start_date = None
    start_time = None
    end_date = None
    end_time = None
    error_message = None

    if request.method == "POST":
        location = request.POST.get("location")
        start_date = request.POST.get("start_date")
        start_time = request.POST.get("start_time")
        end_date = request.POST.get("end_date")
        end_time = request.POST.get("end_time")

        if not all([location, start_date, start_time, end_date, end_time]):
            error_message = "Please fill out all fields, including dates and times."
        else:
            try:
                # Combine date and time into datetime objects
                start_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
                end_datetime = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")

                # Check if end datetime is after start datetime
                if end_datetime <= start_datetime:
                    error_message = "End date and time must be after start date and time."
                else:
                    # Filter halls by location and check availability within the date and time range
                    available_halls = Hall.objects.filter(location__iexact=location)
                    for hall in available_halls:
                        if not Booking.objects.filter(
                            hall=hall,
                            start_time__lt=end_datetime, 
                            end_time__gt=start_datetime
                        ).exists():
                            halls.append(hall)
            except ValueError as e:
                error_message = "Invalid date or time format. Please check your input."

    return render(request, 'check_availability.html', {
        'halls': halls,
        'locations': locations,
        'location': location,
        'start_date': start_date,
        'start_time': start_time,
        'end_date': end_date,
        'end_time': end_time,
        'error_message': error_message,
    })

@login_required
def book_hall(request,hall_id):
    selected_hall = get_object_or_404(Hall, id=hall_id) if hall_id else None
    booking_success = False
    hall_name, location, date = None, None, None

    if request.method == "POST":
        event_name = request.POST.get("event_name")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        booking_date = request.POST.get("booking_date")
        description = request.POST.get("description", "")

        try:
            # Convert datetime strings to Python datetime objects
            start_time = datetime.fromisoformat(start_time)
            end_time = datetime.fromisoformat(end_time)
            booking_date = datetime.strptime(booking_date, "%Y-%m-%d").date()
            no_of_days = (end_time - start_time).days + 1
            total_price = selected_hall.price * no_of_days

        except ValueError:
            messages.error(request, "Invalid date or time format.")
            return redirect('bookings:book_hall', hall_id=selected_hall.id)

        if selected_hall:
            # Check for conflicting bookings
            existing_booking = Booking.objects.filter(
                hall=selected_hall,
                booking_date=booking_date,
                start_time__lt=end_time,
                end_time__gt=start_time,
            )
            if existing_booking.exists():
                messages.error(request, "The hall is already booked for this time slot.")
                return redirect('bookings:book_hall', hall_id=selected_hall.id)
            # Create the new booking
            new_booking = Booking.objects.create(
                hall=selected_hall,
                event_name=event_name,
                start_time=start_time,
                end_time=end_time,
                booking_date=booking_date,
                description=description,
                total_price=total_price,
            )

            booking_success = True
            hall_name = new_booking.hall.name
            location = new_booking.hall.location
            date = new_booking.booking_date

            # Send confirmation email
            send_mail(
                'Booking Confirmation',
                f'Hello {request.user.username},\n\n'
                f'Thank you for booking the {hall_name} for your event "{event_name}".\n'
                f'Your booking has been successfully confirmed for {date} from {start_time} to {end_time}.\n\n'
                'If you have any questions, feel free to contact us.\n\n'
                'Best regards,\nEvent Management Team.',
                'jayanibv@gmail.com',  # Replace with your email
                [request.user.email],
                fail_silently=False,
            )
            return redirect('bookings:payment_page', booking_id=new_booking.id)

    context = {
        'selected_hall': selected_hall,
        'booking_success': booking_success,
        'hall_name': hall_name,
        'location': location,
    }

    return render(request, 'book_hall.html', context)  

def update_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == "POST":
        booking.event_name = request.POST.get("event_name")
        booking.start_time = request.POST.get("start_time")
        booking.end_time = request.POST.get("end_time")
        booking.booking_date = request.POST.get("booking_date")
        booking.description = request.POST.get("description", "")

        # Check for any time conflicts with other bookings for the same hall
        conflicting_bookings = Booking.objects.filter(
            hall=booking.hall,
            booking_date=booking.booking_date,
        ).exclude(id=booking.id).filter(
            start_time__lt=booking.end_time,
            end_time__gt=booking.start_time,
        )

        if conflicting_bookings.exists():
            messages.error(request, "The hall is already booked for this time slot.")
            return redirect('update_booking', booking_id=booking.id)

        # Save updates if no conflicts are found
        booking.save()
        messages.success(request, "Booking updated successfully.")
        return redirect('bookings')  

    return render(request, 'update_booking.html', {'booking': booking})

def update_details(request,booking_id,hall_id):
    if booking_id:
        booking = get_object_or_404(Booking, id=booking_id)
        if request.method == "POST":
            booking.event_name = request.POST.get("event_name")
            booking.description = request.POST.get("description", "")
            booking.save()
            messages.success(request, "Booking details updated successfully.")
            return redirect('bookings')
        return render(request, 'update_details.html', {'booking': booking})
    
    elif hall_id:
        hall = get_object_or_404(Hall, id=hall_id)
        if request.method == "POST":
            form = HallUpdateForm(request.POST, instance=hall)
            if form.is_valid():
                form.save()
                messages.success(request, "Hall details updated successfully.")
                return redirect('hall_details', hall_id=hall.id)
        else:
            form = HallUpdateForm(instance=hall)
        return render(request, 'update_details.html', {'form': form, 'hall': hall})

    return redirect('home')

def update_hall_details(request, hall_id):
    hall = get_object_or_404(Hall, id=hall_id)  # Retrieve hall by ID
    if request.method == 'POST':
        form = HallUpdateForm(request.POST, instance=hall)
        if form.is_valid():
            form.save()  # Save the updates to the database
            return redirect('hall_details', hall_id=hall.id)  # Redirect after successful update
    else:
        form = HallUpdateForm(instance=hall)  # Load the form with current details

    return render(request, 'update_details.html', {'form': form, 'hall': hall})

def bookings(request):
    return render(request, 'bookings.html')

@login_required
def confirm_order(request, booking_id):
    """
    View to confirm the order and redirect to payment options.
    """
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == "POST":
        # Redirect to payment page
        return redirect('payment_page', booking_id=booking.id)

    return render(request, 'confirm_order.html', {'booking': booking})


@login_required
def payment_page(request, booking_id):
    """
    View to handle payment method selection (Credit Card or COD).
    """
    booking = get_object_or_404(Booking, id=booking_id)
    selected_hall = booking.hall
    total_price = booking.total_price
    
    if request.method == "POST":
        # Get the selected payment method
        payment_method = request.POST.get("payment_method")
        if payment_method == "credit_card":
            # Simulate credit card payment
            # (You can integrate with a payment gateway like Stripe, Razorpay, etc.)
            card_number = request.POST.get("card_number")
            expiry_date = request.POST.get("expiry_date")
            cvv = request.POST.get("cvv")

            # Dummy validation for demonstration
            if not card_number or not expiry_date or not cvv:
                messages.error(request, "Credit Card details are incomplete. Please try again.")
                return redirect('payment_page', booking_id=booking.id, total_price=total_price)

            # Assume payment is successful
            booking.payment_status = "Paid"
            booking.payment_method = "Credit Card"
            booking.save()

            messages.success(request, "Payment successful using Credit Card!")
            return redirect('order_confirmation', booking_id=booking.id)

        elif payment_method == "cod":
            # Handle Cash on Delivery (COD)
            booking.payment_status = "Pending"
            booking.payment_method = "Cash on Delivery"
            booking.save()

            messages.success(request, "Order confirmed. Please pay on delivery.")
            return redirect('order_confirmation', booking_id=booking.id)

        else:
            messages.error(request, "Invalid payment method selected. Please try again.")
            return redirect('payment_page', booking_id=booking.id)

    context = {
        "selected_hall": selected_hall,
        "total_price": total_price,
    }
    return render(request, "payment.html", context)


@login_required
def order_confirmation(request, booking_id):
    """
    View to display order confirmation details.
    """
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, "order_confirmation.html", {'booking': booking})


@login_required
def payment_failure(request, booking_id):
    """
    View to display payment failure message.
    """
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, "order_failure.html", {'booking': booking})
