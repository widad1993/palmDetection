from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
#from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from .models import Technician
from .models import Farm, FarmHistory
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
import numpy as np
from PIL import Image
from datetime import datetime
from django.core.files.storage import FileSystemStorage
import cv2
import subprocess
import os
import joblib
import time

with open('base/ml_models/img_model.pkl', 'rb') as file:
    model = joblib.load(file)
    print("Number of features expected by the model:", model.n_features_in_)

# Create your views here.

User = get_user_model()

#@login_required(login_url="/")
def homePage(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")

        if role == "ADMIN":
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("adminPage")
            else:
                messages.error(request, "Invalid username or password.")  

        elif role == "TECH":
            try:
                technician = Technician.objects.get(username=username)
                if check_password(password, technician.password):  
                    request.session["technician_id"] = technician.id
                    return redirect("techPage")
                else:             
                    messages.error(request, "Invalid username or password.")
            except Technician.DoesNotExist:
                   messages.error(request, "Invalid username or password.")

    return render(request, "home_page.html")

def aboutPage(request):
    context = {}
    return render(request, "about_page.html", context= context)


def contactPage(request):
    context = {}
    return render(request, "contact_page.html", context= context)


#@login_required(login_url="/")
def techPage(request):
    technician_id = request.session.get("technician_id")
    if not technician_id:
        return redirect("homePage")  
    
    technician = Technician.objects.get(id=technician_id)
    farms = Farm.objects.all()  
    context = {
        "technician": technician,
        "farms": farms,  
    }
    return render(request, "tech_page.html", context=context)


#@login_required(login_url="/")
def techPageTabel(request, farm_id):
    farm = get_object_or_404(Farm, id=farm_id)
    #history = FarmHistory.objects.filter(farm=farm)

    latest_analysis_ids = request.session.get("latest_analysis_ids", [])

    history = FarmHistory.objects.filter(id__in=latest_analysis_ids)
    # جلب technician_id من الـ session
    technician_id = request.session.get("technician_id")
    if technician_id:
        technician = get_object_or_404(Technician, id=technician_id)
    else:
        technician = None  
    return render(request, "tech_page_tabel.html", {"farm": farm, "history": history, "technician": technician})


#@login_required(login_url="/")
def adminPage(request):
    context = {
        "admin_name": request.user.username  # ✅ جلب اسم المستخدم الحالي
    }
    return render(request, "admin_page.html", context)


#@login_required(login_url="/")
def adminPageTabel(request):
    technicians = Technician.objects.all()
    context = {
        "technicians": technicians ,
        "admin_name": request.user.username  
    }
    return render(request, "admin_page_tabel.html", context=context)

#@login_required(login_url="/")
def add_technician(request):
    if request.method == "POST":
        name = request.POST.get("name")
        username = request.POST.get("username")
        password = request.POST.get("password")

        technician = Technician(
            name=name,
            username=username,
            password=make_password(password),
            plain_password=password     
        )
        technician.save()
        
        return redirect('adminPageTabel')
    
    context = {
        
        "admin_name": request.user.username 
    }

    return render(request, "add_technician.html", context=context)

#@login_required(login_url="/")
def delete_technician(request, technician_id):
    technician = get_object_or_404(Technician, id=technician_id)
    technician.delete()
    return redirect("adminPageTabel")

#@login_required(login_url="/")
def edit_technician(request, technician_id):
    technician = get_object_or_404(Technician, id=technician_id)
    if request.method == "POST":
        technician.name = request.POST.get("name")
        technician.username = request.POST.get("username")
        new_password = request.POST.get("password")
        if new_password and new_password != technician.password:
            technician.password = new_password  
        technician.save()
        return redirect("adminPageTabel")

    context = {
        "technician": technician ,
        "admin_name": request.user.username  
    }
    return render(request, "edit_technician.html", context=context)

#@login_required(login_url="/")
def farmsPage(request):
    context = {
        "admin_name": request.user.username  
    }
    return render(request, "farms_page.html", context= context)


#@login_required(login_url="/")
def farmsPageTabel(request):
    farms = Farm.objects.all()  
    context = {
        'farms': farms ,
        "admin_name": request.user.username  
    }
    return render(request, "farms_page_tabel.html", context=context)

#@login_required(login_url="/")
def end_analysis(request, farm_id):
    try:
        
        farm = get_object_or_404(Farm, id=farm_id)

        messages.success(request, "Analysis has been ended successfully.")
    except Exception as e:
        
        messages.error(request, f"Error while ending analysis: {e}")

    return redirect("techPage")


#@login_required(login_url="/")
def add_farm(request):
    if request.method == "POST":
        name = request.POST.get("name")
        owner = request.POST.get("owner")
        city = request.POST.get("city")
        location = request.POST.get("location")
        subscription = request.POST.get("subscription")

        Farm.objects.create(
            name=name,
            owner=owner,
            city=city,
            location=location,
            subscription=subscription,
        )
        
        return redirect("farmsPageTabel")
    context = {
        
        "admin_name": request.user.username  
    }
    return render(request, "add_farm.html", context=context)

#@login_required(login_url="/")
def delete_farm(request, farm_id):
    farm = get_object_or_404(Farm, id=farm_id)
    farm.delete()
    return redirect("farmsPageTabel")

#@login_required(login_url="/")
def edit_farm(request, farm_id):
    farm = get_object_or_404(Farm, id=farm_id)
    if request.method == "POST":
        farm.name = request.POST.get("name")
        farm.owner = request.POST.get("owner")
        farm.city = request.POST.get("city")
        farm.location = request.POST.get("location")
        farm.subscription = request.POST.get("subscription")
        farm.save()
        return redirect("farmsPageTabel")

    context = {
        "farm": farm ,
        "admin_name": request.user.username  
    }
    return render(request, "edit_farm.html", context=context)

#@login_required(login_url="/")
def farmsPageDate(request, farm_id):
    farm = get_object_or_404(Farm, id=farm_id)
    history_records = FarmHistory.objects.filter(farm=farm)

    context = {
        "farm": farm,
        "history_records": history_records,
        "admin_name": request.user.username  
    }
    return render(request, "farms_page_date.html", context=context)


def process_video(video_file, request):
    try:
        if video_file:
            fs = FileSystemStorage()
            file_path = fs.save(video_file.name, video_file)
            video_path = fs.path(file_path)
        else:
            raise Exception("No video file provided!")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Unable to open video file. Please check the file path or format.")

        frame_count = 0
        image_links = []  

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 30 
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count) 
            try:
                resized_frame = cv2.resize(frame, (150, 150))
                frame_array = np.array(resized_frame) / 255.0  
                
                if frame_array.shape[-1] != 3:
                    frame_array = np.stack((frame_array,) * 3, axis=-1)

                frame_array_flattened = frame_array.flatten().reshape(1, -1)

                prediction = model.predict(frame_array_flattened)[0]  
                damage_type = "Palm Weevil" if prediction == 1 else "Healthy Palm"

               
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'images'))
                image_name = f"frame_{frame_count}.jpg"
                image_path = fs.path(image_name)
                cv2.imwrite(image_path, frame)

               
                image_link = request.build_absolute_uri(settings.MEDIA_URL + f"images/{image_name}")
                image_links.append((image_link, damage_type)) 

                print(f"Frame {frame_count}: {damage_type} - {image_link}")

            except Exception as frame_error:
                print(f"Error processing frame {frame_count}: {frame_error}")
                continue

        cap.release()
        return image_links  

    except Exception as e:
        print(f"Error processing video: {e}")
        return []



def process_live_stream(stream_url, request):
    try:
        cap = cv2.VideoCapture(stream_url)

        if not cap.isOpened():
            raise Exception("Unable to access live stream URL.")

        damage_type = "Unknown"
        location = "Unknown"
        frame_count = 0
        image_links = []  

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("No frames received from live stream.")
                break

            frame_count += 1

            # Process every 1 second (30 frames if 30 FPS)
            if frame_count % 30 == 0:
                try:
                    resized_frame = cv2.resize(frame, (150, 150))
                    frame_array = np.array(resized_frame) / 255.0  

                    # Ensure the image has 3 channels
                    if frame_array.shape[-1] != 3:
                        frame_array = np.stack((frame_array,) * 3, axis=-1)

                    # Reshape data for model input
                    frame_array_flattened = frame_array.flatten().reshape(1, -1)

                    # Predict using the model
                    prediction = model.predict(frame_array_flattened)

                    # Check if damage is detected
                    if prediction.size > 0 and prediction[0] == 1:  
                        damage_type = "Palm Weevil"
                        location = "Live GPS Coordinates (Simulated)"

                        # Save the image if damage is detected
                        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'images'))
                        image_name = f"live_frame_{frame_count}.jpg"
                        image_path = fs.path(image_name)

                        cv2.imwrite(image_path, frame)  

                        # Generate a URL for the saved image
                        image_link = request.build_absolute_uri(settings.MEDIA_URL + f"images/{image_name}")
                        image_links.append(image_link)  
                        print(f"Damage detected! Image saved: {image_link}")

                    else:
                        damage_type = "Healthy Palm"

                except Exception as frame_error:
                    print(f"Error processing frame {frame_count}: {frame_error}")
                    continue  

            time.sleep(1)  

        cap.release()

        return damage_type, location, image_links  

    except Exception as e:
        print(f"Error processing live stream: {e}")
        return "Error", "Unknown", []


#@login_required(login_url="/")
def analyze_drone_images(request):
    if request.method == "POST":
        drone_url = request.POST.get("drone_url")
        farm_id = request.POST.get("farm_id")
        video_file = request.FILES.get("video_file")

        if not drone_url and not video_file:
            messages.error(request, "Please enter either a live feed URL or upload a video file.")
            return redirect("techPage")

        if not farm_id:
            messages.error(request, "Please select a farm.")
            return redirect("techPage")

        farm = get_object_or_404(Farm, id=farm_id)

        try:
            
            if video_file:
                image_links = process_video(video_file, request)
            elif drone_url:
                image_links = process_live_stream(drone_url)

            if not image_links:
                messages.error(request, "No frames were processed.")
                return redirect("techPage")

            new_analysis_ids = []

            
            for img_link, damage_type in image_links:  
                new_record = FarmHistory.objects.create(
                    farm=farm,
                    image=img_link,
                    damage_type=damage_type,  
                    location="Unknown",  
                    timestamp=datetime.now()
                )
                new_analysis_ids.append(new_record.id)
                print(f"✅ Stored Image in DB: {img_link} - Type: {damage_type}")

            request.session["latest_analysis_ids"] = new_analysis_ids

            messages.success(request, "Analysis completed successfully.")
            return redirect("techPageTabel", farm_id=farm.id)

        except Exception as e:
            messages.error(request, f"Error during analysis: {e}")
            return redirect("techPage")

