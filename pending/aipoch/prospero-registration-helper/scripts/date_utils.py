import datetime

def get_timeline():
    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(days=28)
    return {
        "start_date": start_date.strftime("%d/%m/%Y"),
        "end_date": end_date.strftime("%d/%m/%Y")
    }

if __name__ == "__main__":
    timeline = get_timeline()
    print(f"Start Date: {timeline['start_date']}")
    print(f"Anticipated Completion Date: {timeline['end_date']}")
