/* LifePulse Frontend Application JS */

// Toggle Donor Availability in Header (Matching Screenshot 1)
function toggleDonorStatus() {
    const btn = document.getElementById('statusToggleBtn');
    const dot = document.getElementById('statusIndicatorDot');
    const text = document.getElementById('statusText');

    fetch('/api/toggle-status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            text.innerText = data.new_status;
            if (data.new_status === 'Available') {
                btn.className = "px-3 py-1.5 rounded-lg border text-xs sm:text-sm font-medium flex items-center gap-2 transition-all cursor-pointer shadow-2xs hover:bg-gray-50 border-emerald-200 bg-emerald-50 text-emerald-800";
                dot.className = "w-2.5 h-2.5 rounded-full bg-emerald-500 ring-2 ring-emerald-200 animate-pulse";
                showNotification("Status updated: You are now Available to receive donor requests!", "success");
            } else {
                btn.className = "px-3 py-1.5 rounded-lg border text-xs sm:text-sm font-medium flex items-center gap-2 transition-all cursor-pointer shadow-2xs hover:bg-gray-50 border-gray-200 bg-gray-100 text-gray-700";
                dot.className = "w-2.5 h-2.5 rounded-full bg-gray-400";
                showNotification("Status updated: You are marked as Temporarily Unavailable.", "info");
            }
        }
    })
    .catch(err => {
        console.error("Error toggling status:", err);
    });
}

// Geolocation Handling for "Use GPS Location" Button
function useCurrentLocation() {
    const gpsBtn = document.getElementById('gpsBtn');
    const locationInput = document.getElementById('locationInput');
    
    if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser. Please type your city name.");
        return;
    }

    const originalContent = gpsBtn.innerHTML;
    gpsBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin text-slate-600"></i> Locating...';

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            gpsBtn.innerHTML = '<i class="fa-solid fa-check text-emerald-600"></i> Located';
            locationInput.value = `${lat.toFixed(3)}, ${lng.toFixed(3)} (Current GPS)`;
            showNotification(`GPS coordinates acquired (${lat.toFixed(2)}, ${lng.toFixed(2)})`, "success");
            setTimeout(() => {
                gpsBtn.innerHTML = originalContent;
            }, 2500);
        },
        (error) => {
            console.warn("GPS access denied/unavailable, providing simulated location:", error.message);
            // Graceful fallback for local development:
            gpsBtn.innerHTML = '<i class="fa-solid fa-location-dot text-primary-600"></i> Default Loc';
            locationInput.value = "New York";
            showNotification("Location defaulted to New York for demo", "info");
            setTimeout(() => {
                gpsBtn.innerHTML = originalContent;
            }, 2000);
        },
        { timeout: 7000 }
    );
}

// Modal Handlers: Urgent Need
function openUrgentModal() {
    const modal = document.getElementById('urgentNeedModal');
    if (modal) modal.classList.remove('hidden');
}

function closeUrgentModal() {
    const modal = document.getElementById('urgentNeedModal');
    if (modal) modal.classList.add('hidden');
}

// Modal Handlers: Contact Donor
function openContactModal(name, bloodGroup, city, phone) {
    const modal = document.getElementById('contactDonorModal');
    document.getElementById('modalDonorName').innerText = name;
    document.getElementById('modalBloodGroup').innerText = bloodGroup;
    document.getElementById('modalLocation').innerText = city;
    
    const callBtn = document.getElementById('modalCallBtn');
    callBtn.href = `tel:${phone}`;
    
    const waBtn = document.getElementById('modalWhatsappBtn');
    const message = encodeURIComponent(`Hello ${name}, I found your contact on LifePulse. We have an urgent blood requirement for blood group ${bloodGroup}. Are you currently available to donate?`);
    // Clean numeric phone for whatsapp
    const cleanPhone = phone.replace(/[^0-9]/g, '');
    waBtn.href = `https://wa.me/${cleanPhone}?text=${message}`;

    if (modal) modal.classList.remove('hidden');
}

function closeContactModal() {
    const modal = document.getElementById('contactDonorModal');
    if (modal) modal.classList.add('hidden');
}

// Quick Alert Notification Simulation
function sendQuickAlertNotice() {
    showNotification("🚨 Emergency notification sent directly to donor's phone!", "success");
    setTimeout(closeContactModal, 1500);
}

// Share Urgent Need
function shareUrgentNeed(patient, group, hospital) {
    const shareText = `🚨 Urgent Blood Needed!\nPatient: ${patient}\nBlood Group: ${group}\nHospital: ${hospital}\nPlease check or respond on LifePulse: ${window.location.origin}/urgent-needs`;
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(shareText).then(() => {
            showNotification("Emergency link & details copied to clipboard!", "success");
        });
    } else {
        alert(shareText);
    }
}

function simulateLogout() {
    showNotification("Logged out of demo session. Log back in anytime with demo account 'nihil'.", "info");
}

// Custom Toast Notification Helper
function showNotification(message, type = 'info') {
    const toast = document.createElement('div');
    const bgClass = type === 'success' ? 'bg-emerald-600 text-white' : type === 'danger' ? 'bg-red-600 text-white' : 'bg-slate-900 text-white';
    
    toast.className = `fixed bottom-6 right-6 z-50 px-4 py-3 rounded-xl shadow-2xl text-xs sm:text-sm font-semibold flex items-center gap-2.5 transition-all transform translate-y-4 opacity-0 ${bgClass}`;
    toast.innerHTML = `<i class="fa-solid fa-circle-check"></i> <span>${message}</span>`;
    
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.classList.remove('translate-y-4', 'opacity-0');
    }, 50);

    setTimeout(() => {
        toast.classList.add('translate-y-4', 'opacity-0');
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

// Leaflet Map Initialization
function initLeafletMap(containerId) {
    const container = document.getElementById(containerId);
    if (!container || typeof L === 'undefined') return;

    // Center map around a global/regional hub (or first marker)
    const map = L.map(containerId).setView([39.8283, -98.5795], 4);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    fetch('/api/map-data')
        .then(res => res.json())
        .then(data => {
            const bounds = [];

            // Add Donors (Red circle markers)
            data.donors.forEach(donor => {
                if (donor.latitude && donor.longitude) {
                    bounds.push([donor.latitude, donor.longitude]);
                    
                    const donorIcon = L.divIcon({
                        className: 'custom-leaflet-donor',
                        html: `<span>${donor.blood_group}</span>`,
                        iconSize: [32, 32],
                        iconAnchor: [16, 16]
                    });

                    L.marker([donor.latitude, donor.longitude], { icon: donorIcon })
                        .addTo(map)
                        .bindPopup(`
                            <div style="font-size: 12px; font-family: Inter, sans-serif;">
                                <div style="font-weight: 800; font-size: 14px; margin-bottom: 2px;">${donor.name}</div>
                                <div style="color: #dc2626; font-weight: 700; margin-bottom: 4px;">Blood Group: ${donor.blood_group}</div>
                                <div style="color: #64748b; margin-bottom: 8px;">📍 ${donor.city}</div>
                                <a href="tel:${donor.phone}" style="display: block; background: #dc2626; color: #fff; text-align: center; padding: 4px 8px; border-radius: 6px; font-weight: 700; text-decoration: none;">
                                    📞 Call Donor (${donor.phone})
                                </a>
                            </div>
                        `);
                }
            });

            // Add Urgent Hospital Requests (Dark ambulance markers)
            data.urgent_requests.forEach(req => {
                if (req.latitude && req.longitude) {
                    bounds.push([req.latitude, req.longitude]);
                    
                    const hospitalIcon = L.divIcon({
                        className: 'custom-leaflet-hospital',
                        html: `<i class="fa-solid fa-hospital text-red-500"></i>`,
                        iconSize: [36, 36],
                        iconAnchor: [18, 18]
                    });

                    L.marker([req.latitude, req.longitude], { icon: hospitalIcon })
                        .addTo(map)
                        .bindPopup(`
                            <div style="font-size: 12px; font-family: Inter, sans-serif;">
                                <div style="background: #fee2e2; color: #991b1b; display: inline-block; padding: 2px 6px; border-radius: 4px; font-weight: 800; font-size: 10px; margin-bottom: 4px;">
                                    ${req.urgency_level}
                                </div>
                                <div style="font-weight: 800; font-size: 14px; color: #0f172a;">${req.hospital_name}</div>
                                <div style="margin: 4px 0; color: #334155;">
                                    Patient: <strong>${req.patient_name}</strong><br>
                                    Needed: <strong style="color: #dc2626;">${req.blood_group}</strong> (${req.units_needed} Units)
                                </div>
                                <a href="tel:${req.hotline}" style="display: block; background: #0f172a; color: #fff; text-align: center; padding: 4px 8px; border-radius: 6px; font-weight: 700; text-decoration: none; margin-top: 6px;">
                                    🚨 Hospital Hotline (${req.hotline})
                                </a>
                            </div>
                        `);
                }
            });

            // Fit map bounds if markers exist
            if (bounds.length > 0) {
                map.fitBounds(bounds, { padding: [50, 50], maxZoom: 13 });
            }
        })
        .catch(err => console.error("Map data fetch error:", err));
}

// Mobile Menu Drawer Toggle
function toggleMobileMenu() {
    const menu = document.getElementById('mobileMenu');
    if (menu) {
        menu.classList.toggle('hidden');
    }
}

// Volunteer to Donate Modal Handlers
function openVolunteerModal(reqId, patientName, bloodGroup, hospitalName) {
    const modal = document.getElementById('volunteerModal');
    const reqInput = document.getElementById('volRequestId');
    const subText = document.getElementById('volModalSub');
    
    if (reqInput) reqInput.value = reqId;
    if (subText) subText.innerText = `Pledge unit for ${patientName} (${bloodGroup}) at ${hospitalName}`;
    if (modal) modal.classList.remove('hidden');
}

function closeVolunteerModal() {
    const modal = document.getElementById('volunteerModal');
    if (modal) modal.classList.add('hidden');
}

function submitVolunteerPledge(e) {
    e.preventDefault();
    const form = document.getElementById('volunteerForm');
    const formData = new FormData(form);
    const reqId = formData.get('request_id');

    fetch('/api/respond-urgent', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            closeVolunteerModal();
            showNotification(data.message, "success");

            // Update UI elements in place in real time
            const countEl = document.getElementById(`pledge-count-${reqId}`);
            const pctEl = document.getElementById(`pledge-pct-${reqId}`);
            const barEl = document.getElementById(`pledge-bar-${reqId}`);

            if (countEl && pctEl && barEl) {
                countEl.innerText = data.units_fulfilled;
                const pct = Math.min(100, Math.round((data.units_fulfilled / data.units_needed) * 100));
                pctEl.innerText = `${pct}%`;
                barEl.style.width = `${pct}%`;
                if (pct >= 100) {
                    barEl.className = "h-full bg-emerald-500 rounded-full transition-all duration-500";
                }
            }
        } else {
            showNotification(data.message || "Could not record pledge.", "danger");
        }
    })
    .catch(err => {
        console.error("Error submitting volunteer pledge:", err);
        showNotification("Failed to connect to emergency dispatch server.", "danger");
    });
}

// Close modals when clicking backdrop
window.addEventListener('click', function(e) {
    const urgentModal = document.getElementById('urgentNeedModal');
    const contactModal = document.getElementById('contactDonorModal');
    const volunteerModal = document.getElementById('volunteerModal');
    if (e.target === urgentModal) closeUrgentModal();
    if (e.target === contactModal) closeContactModal();
    if (e.target === volunteerModal) closeVolunteerModal();
});

