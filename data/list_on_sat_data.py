"""Data-driven vehicle records for the Sell My Car > List on SAT tests."""

from pathlib import Path


IMAGES_DIR = Path(__file__).resolve().parents[1] / "assets" / "images"


def image_paths(*filenames):
    return [str(IMAGES_DIR / filename) for filename in filenames]


def listing(
    make,
    model,
    year,
    color,
    mileage,
    price,
    engine,
    transmission,
    images,
    *,
    fuel="Petrol",
    drivetrain="2WD",
    seats="5 Seats",
    description="Used vehicle in good condition with clean interior and well-maintained components.",
):
    """Build a listing while keeping shared form values in one place."""
    return {
        "make": make,
        "model": model,
        "year": str(year),
        "fuel": fuel,
        "steering": "RHD",
        "drivetrain": drivetrain,
        "seats": seats,
        "country": "United Kingdom",
        "city": "Bristol",
        "color": color,
        "mileage": str(mileage),
        "price": str(price),
        "engine": str(engine),
        "transmission": transmission,
        "description": description,
        "phone": "+447412000000",
        "images": image_paths(*images),
    }


LIST_ON_SAT_PARAMS = [
    # Only makes and models verified as available in the SAT dropdowns.
    listing("Honda", "ZEST SPARK", 2010, "Silver", 98000, 620000, 660, "AT", ["2010 Honda Zest Spark Silver.jpg"], seats="4 Seats"),
    listing("Nissan", "Wingroad", 2016, "Silver", 61000, 1150000, 1500, "AT", ["2016 Nissan Wingroad AT Silver.jpg"]),
    listing("Honda", "VEZEL", 2020, "White", 31000, 2850000, 1500, "CVT", ["Honda Vezel White.jpg"]),
    listing("Honda", "Z", 2021, "White", 22000, 3900000, 1500, "CVT", ["Honda ZR-V E White.jpeg"]),
    listing("Mazda", "VERISA", 2014, "Black", 72000, 880000, 1500, "AT", ["Mazda Verisa Black.png"]),
    listing("Mazda", "VERISA", 2013, "Red", 79000, 760000, 1500, "AT", ["Mazda Verisa Red.jpg"]),
    listing("Nissan", "X-TRAIL", 2019, "Orange", 43000, 2750000, 2000, "CVT", ["Nissan X-Trail Orange.jpeg"]),
    listing(
        "Nissan", "X-TRAIL", 2018, "White", 51000, 2480000, 2000, "CVT",
        [
            "Nissan X-TRAIL White 1.jpg",
            "Nissan X-TRAIL White 2.jpg",
            "Nissan X-TRAIL White 3.jpg",
            "Nissan X-TRAIL White 4.jpg",
            "Nissan X-TRAIL White 6.jpg",
        ],
    ),
    listing("Nissan", "X-TRAIL", 2021, "Grey", 26000, 3350000, 2000, "CVT", ["Nissan-X-Trail-2021.png"]),
    listing("Suzuki", "ALTO", 2015, "Red", 68000, 590000, 660, "CVT", ["Suzuki Alto Red.jpeg"], seats="4 Seats"),
    listing("Suzuki", "ALTO", 2017, "White", 52000, 740000, 660, "CVT", ["Suzuki Alto White.jpeg"], seats="4 Seats"),
    listing("Suzuki", "WAGON R", 2016, "White", 59000, 920000, 660, "CVT", ["Suzuki Wagon R - White.jpg"], seats="4 Seats"),
    listing("Suzuki", "X BEE", 2020, "White", 29000, 1950000, 1000, "CVT", ["Suzuki X BEE White.jpg"], seats="4 Seats"),
    listing("Suzuki", "X-90", 2011, "White", 86000, 1250000, 1600, "AT", ["Suzuki X-90 White.jpg"], drivetrain="4WD(AWD)", seats="2 Seats"),
    listing("Toyota", "ALLION", 2015, "Red", 64000, 1650000, 1800, "CVT", ["Toyota Allion Red 1.jpg", "Toyota Allion red 2.jpg"]),
    listing("Toyota", "AQUA", 2018, "White", 47000, 1450000, 1500, "CVT", ["Toyota Aqua White 1.jpeg", "Toyota Aqua White 2.jpeg", "Toyota Aqua White 3.jpeg"], fuel="Hybrid"),
    listing("Toyota", "YARIS", 2026, "Silver", 3000, 4200000, 1500, "CVT", ["Toyota Yaris Sedan 2026 Silver.png"]),
]


def _assert_unique_listings():
    identities = [(item["make"], item["model"], item["color"]) for item in LIST_ON_SAT_PARAMS]
    if len(identities) != len(set(identities)):
        raise ValueError("Duplicate List on SAT vehicle found (make, model, color)")


_assert_unique_listings()
