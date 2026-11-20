"""Desktop and mobile navigation for the Car Services menu."""

from urllib.parse import urlparse


class CarServicesPage:
    DESTINATIONS = {
        "auction": (
            "Auction Service",
            "/sat-auction",
            ".auction-service-overview",
        ),
        "shipping": (
            "Shipping Schedule",
            "/shipping-schedule",
            "p.see-first-para",
        ),
        "warranty": (
            "Warranty Service",
            "/sat-warranty",
            "h1:has-text('SAT Japan Warranty')",
        ),
        "storage": (
            "Storage Service",
            "/storage-policy",
            "h1:has-text('Secure Storage Service')",
        ),
        "finance": (
            "Finance Service",
            "/finance-services",
            "h1:has-text('Enjoy flexible payment options')",
        ),
        "carrier": (
            "Car Carrier Service",
            "/car-carrier",
            "h1:has-text('Get your vehicle delivered')",
        ),
        "customs": (
            "Custom Clearance",
            "/customs-clearance",
            "h1:has-text('Ensure Fast and Compliant Shipments')",
        ),
        "pre_export": (
            "Pre Export Inspection",
            "/pre-export-inspection",
            "h1:has-text('Seal The Deal With Pre-Export Inspection')",
        ),
        "marine": (
            "Marine Insurance Service",
            "/marine-insurance-services",
            "h1:has-text('Get full coverage up to the cost')",
        ),
        "non_stolen": (
            "Non Stolen Vehicle Check",
            "/non-stolen-vehicle",
            "h2.nsb__title:has-text('Get a verified non-stolen vehicle certificate')",
        ),
    }

    def __init__(self, page):
        self.page = page

    def _wait_for_destination(self, key):
        _, path, ready_selector = self.DESTINATIONS[key]
        self.page.wait_for_url(f"**{path}*", wait_until="domcontentloaded")
        self.page.locator(ready_selector).first.wait_for(state="visible")
        assert urlparse(self.page.url).path.rstrip("/") == path

    def _go_desktop(self, key):
        _, path, _ = self.DESTINATIONS[key]
        label = self.page.locator("p.cnm-cls", has_text="Car Services").first
        label.wait_for(state="visible")
        label.hover()

        # Scope by destination URL inside the Car Services dropdown. This
        # avoids duplicate accessible names elsewhere in the header/footer.
        menu = label.locator("xpath=..")
        link = menu.locator(f"a[href$='{path}']").first
        link.wait_for(state="visible")
        link.click()
        self._wait_for_destination(key)
        return self

    def _open_mobile_menu(self):
        toggle = self.page.locator(
            "#menu_logo_mobile span[data-bs-target='#sidebarmobile']"
        )
        toggle.wait_for(state="visible")

        main_menu = self.page.locator("#sidebarmobile")
        if not main_menu.is_visible():
            toggle.click()
            main_menu.wait_for(state="visible")

        services_link = main_menu.locator(
            "a.main-items-sidebar-content",
            has_text="Car Services",
        ).first
        target = services_link.get_attribute("href") or ""
        assert target.startswith("#"), (
            f"Mobile Car Services menu target changed: {target!r}."
        )
        submenu = self.page.locator(target)
        if not submenu.is_visible():
            services_link.click()
            submenu.wait_for(state="visible")
        return submenu

    def _go_mobile(self, key):
        _, path, _ = self.DESTINATIONS[key]
        submenu = self._open_mobile_menu()
        link = submenu.locator(f"a[href$='{path}']").first
        link.wait_for(state="visible")
        link.click()
        self._wait_for_destination(key)
        assert self.page.locator("#navbar_mobile_header").is_visible()
        return self

    def get_mobile_menu_contract(self):
        submenu = self._open_mobile_menu()
        expected_paths = {
            destination[1] for destination in self.DESTINATIONS.values()
        }
        links = submenu.get_by_role("link")
        return [
            {
                "name": " ".join(link.inner_text().split()),
                "path": urlparse(link.get_attribute("href") or "").path,
            }
            for link in links.all()
            if urlparse(link.get_attribute("href") or "").path
            in expected_paths
        ]

    def go_to_auction_service(self):
        return self._go_desktop("auction")

    def go_to_shipping_schedule(self):
        return self._go_desktop("shipping")

    def go_to_warranty_service(self):
        return self._go_desktop("warranty")

    def go_to_storage_service(self):
        return self._go_desktop("storage")

    def go_to_finance_service(self):
        return self._go_desktop("finance")

    def go_to_car_carrier_service(self):
        return self._go_desktop("carrier")

    def go_to_customs_clearance(self):
        return self._go_desktop("customs")

    def go_to_pre_export_inspection(self):
        return self._go_desktop("pre_export")

    def go_to_marine_insurance(self):
        return self._go_desktop("marine")

    def go_to_non_stolen_vehicle(self):
        return self._go_desktop("non_stolen")

    def go_to_auction_service_mobile(self):
        return self._go_mobile("auction")

    def go_to_shipping_schedule_mobile(self):
        return self._go_mobile("shipping")

    def go_to_warranty_service_mobile(self):
        return self._go_mobile("warranty")

    def go_to_pre_export_inspection_mobile(self):
        return self._go_mobile("pre_export")

    def go_to_non_stolen_vehicle_mobile(self):
        return self._go_mobile("non_stolen")
