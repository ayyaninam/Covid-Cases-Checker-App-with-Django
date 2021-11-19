from django.shortcuts import render, redirect
import requests
from geopy import Nominatim
from django.contrib import messages
from .fips_dict import fips
# import all the libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.switch_backend('agg')
def home(request):
    context= {}
    if request.method == "POST":
        valLatLng = request.POST.get("valLatLng")
        geolocator = Nominatim(user_agent='test/1')
        location = geolocator.reverse(f"{valLatLng[7:-1]}")
        try:
            address = location.address
            print(address)
        except:
            return redirect("home")

        for key,value in fips.items():
            try:
                if value[1] in address.split(", ") and value[0] in address.split(", "):
                    print("yes")
                    state = f"{value}"
                    fipskey = f"{key}"

                    messages.success(request, 'Your Fips Code is: '+ fipskey)
            except:
                state = ""
                messages.error(request, "Sorry we can't find your fips code")
                


        context.update({
            "latcc":valLatLng[7:-1].split(", ")[0],
            "lngcc":valLatLng[7:-1].split(", ")[1],
        })
        
    return render(request, "home.html", context)

# Create your views here.
def search(request):
    if request.method == "POST":
        zip_code = request.POST.get("zip_code")
        date = request.POST.get("date")
        latitude_lng_value = request.POST.get("latitude_lng_value")
        context = {
            "date":date,
            "zip_code":zip_code,
            "llat":latitude_lng_value[7:-1].split(", ")[0],
            "llng":latitude_lng_value[7:-1].split(", ")[1]
        }
        # api_search_state = fips[f"{zip_code}"]
        resp = requests.get(f"https://api.covidactnow.org/v2/county/{zip_code}.timeseries.json?apiKey=73c4080ffa4c4b5282b729c4a2420db0")

        if resp.status_code != 200:
            zero = "True"
            context.update({
                "zero":zero
            })
            print(zero)

        else:
            data1 = resp.json()
            state = data1["state"]
            county = data1["county"]
            country = data1["country"]
            fips = data1["fips"]
            population = data1["population"]

            context.update({
                "state":state,
                "county":county,
                "country":country,
                "fips":fips,
                "population":population,
            })

            data2 = (data1["actualsTimeseries"])
            cases_data = {
                    "date_roll": [],
                    "cases": []
            }
            deaths_data = {
                "date_roll": [],
                "deaths": [],
            }
            for index, confirm_data in enumerate(data2):
                cases_data["date_roll"].append(index+1)
                
                cases_data["cases"].append(confirm_data["newCases"] if confirm_data["newCases"] != None else int(0))

                deaths_data["date_roll"].append(index+1)
                deaths_data["deaths"].append(confirm_data["newDeaths"] if confirm_data["newCases"] != None else int(0))
                if (confirm_data["date"] == date):
                    context.update({"data":confirm_data})


            df1 = pd.DataFrame(cases_data)
            x1 = np.array(df1["date_roll"])
            y1 = np.array(df1["cases"])
            plt.plot(x1,y1)
            plt.ylabel("Daily Cases")
            plt.xlabel("Date")
            ax1 = plt.gca()
            fig1 =plt.gcf()
            fig1.set_size_inches(20, 5.2)
            ax1.axes.xaxis.set_ticklabels([])
            ax1.axes.yaxis.set_ticklabels([])
            plt.savefig('static/images/Trends/demo_waste.jpg')
            plt.close() 



            


            df2 = pd.DataFrame(deaths_data)
            x2 = np.array(df2["date_roll"])
            y2 = np.array(df2["deaths"])
            plt.plot(x2,y2, "r-")
            plt.ylabel("Daily Deaths")
            plt.xlabel("Date")
            ax2 = plt.gca()
            fig2 =plt.gcf()
            fig2.set_size_inches(20, 5.2)
            ax2.axes.xaxis.set_ticklabels([])
            ax2.axes.yaxis.set_ticklabels([])
            plt.savefig('static/images/Trends/demo_waste_1.jpg')
            plt.close() 



        


    return render(request, "search.html",context)