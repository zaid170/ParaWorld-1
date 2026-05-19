document.addEventListener('DOMContentLoaded', () => {

    // --- 1. DYNAMIC NAVIGATION COLOR SHIFT ON SCROLL ---
    // Automatically darkens the navbar when scrolling down for better readability
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 40) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // --- 2. MOBILE NAVIGATION DRAWER TOGGLE ---
    // Smoothly slides in the mobile navigation menu and transforms the hamburger into an "X"
    const hamburgerMenu = document.getElementById('hamburger-menu');
    const navDrawer = document.getElementById('nav-drawer');

    hamburgerMenu.addEventListener('click', () => {
        navDrawer.classList.toggle('active');
        
        // Toggle bar shapes for Close mark "X"
        const bars = hamburgerMenu.querySelectorAll('div');
        if (navDrawer.classList.contains('active')) {
            bars[0].style.transform = 'rotate(45deg) translate(6px, 6px)';
            bars[1].style.opacity = '0';
            bars[2].style.transform = 'rotate(-45deg) translate(6px, -6px)';
        } else {
            bars[0].style.transform = 'none';
            bars[1].style.opacity = '1';
            bars[2].style.transform = 'none';
        }
    });

    // Automatically close the mobile menu drawer when any link inside it is clicked
    navDrawer.querySelectorAll('a').forEach(anchor => {
        anchor.addEventListener('click', () => {
            navDrawer.classList.remove('active');
            const bars = hamburgerMenu.querySelectorAll('div');
            bars[0].style.transform = 'none';
            bars[1].style.opacity = '1';
            bars[2].style.transform = 'none';
        });
    });

    // --- 3. CLASSROOM SECTION - INTERACTIVE TAB DATA ENGINE ---
    // Dynamically updates classroom environment previews when clicking different feature tabs
    const tabs = document.querySelectorAll('.classroom-tab');
    const displayWindow = document.getElementById('display-window');

    const contentMap = {
        smart: {
            icon: "🏫",
            title: "Focus-Oriented Seating",
            text: "Study in spacious layouts designed to allow teachers to monitor every individual's notebook while keeping seating highly comfortable for long batches."
        },
        heating: {
            icon: "🔥",
            title: "Cozy Winter Heating Support",
            text: "Shopian winters are cold, but our studies never pause. Our classroom environment stays warm and comfortable to make sure you never lose focus due to freezing weather."
        },
        boards: {
            icon: "🖊️",
            title: "Smart Teaching Boards",
            text: "Our physical whiteboards are clean, glare-free, and matched with colorful interactive illustrations from teachers to explain formulas and science mechanisms clearly."
        }
    };

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Reset active state classes across all tabs
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Pull corresponding text information matching the data-content attribute
            const key = tab.getAttribute('data-content');
            const data = contentMap[key];

            // Trigger a smooth scaling fade transition out
            displayWindow.style.opacity = '0';
            displayWindow.style.transform = 'scale(0.95)';

            setTimeout(() => {
                // Insert new tab information dynamically
                displayWindow.innerHTML = `
                    <span class="display-icon">${data.icon}</span>
                    <h3>${data.title}</h3>
                    <p>${data.text}</p>
                `;
                // Smooth scaling fade in
                displayWindow.style.opacity = '1';
                displayWindow.style.transform = 'scale(1)';
            }, 300);
        });
    });

    // --- 4. INTERACTIVE FACULTY FILTERS ---
    // Smoothly filters out faculty cards based on subject departments
    const filterBtns = document.querySelectorAll('.filter-btn');
    const cards = document.querySelectorAll('.teacher-card');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state on department selector buttons
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const department = btn.getAttribute('data-filter');

            cards.forEach(card => {
                const category = card.getAttribute('data-category');

                if (department === 'all' || category === department) {
                    card.classList.remove('hidden');
                    setTimeout(() => {
                        card.style.transform = 'scale(1)';
                        card.style.opacity = '1';
                    }, 50);
                } else {
                    card.style.transform = 'scale(0.85)';
                    card.style.opacity = '0';
                    setTimeout(() => {
                        card.classList.add('hidden');
                    }, 300);
                }
            });
        });
    });

    // --- 5. FAQ ACCORDION ENGINE ---
    // Smoothly reveals and hides answer cards for Frequently Asked Questions
    const questions = document.querySelectorAll('.faq-question');
    questions.forEach(q => {
        q.addEventListener('click', () => {
            const item = q.parentElement;
            const isActive = item.classList.contains('active');

            // Close any other open FAQ items for a clean accordion effect
            document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('active'));

            if (!isActive) {
                item.classList.add('active');
            }
        });
    });

    // --- 6. ADMISSION ENQUIRY SUBMISSION (AJAX ROUTING) ---
    // Submits the standard admissions form dynamically to your Python Flask backend
    const form = document.getElementById('enquiryForm');
    const modal = document.getElementById('modalWindow');
    const dismissBtn = document.getElementById('dismissModalBtn');

    if (form) {
        form.addEventListener('submit', async (event) => {
            event.preventDefault(); // Prevents standard page refreshes

            // Gather inputs cleanly
            const studentName = document.getElementById('studentName').value;
            const studentPhone = document.getElementById('studentPhone').value;
            const gradeSelection = document.getElementById('gradeSelection').value;

            try {
                // Fetch request to Python backend
                const response = await fetch('/submit-enquiry', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        name: studentName,
                        phone: studentPhone,
                        grade: gradeSelection
                    })
                });

                const result = await response.json();

                if (response.ok && result.status === 'success') {
                    // Launch custom premium success popup modal
                    modal.classList.add('active');
                    form.reset();
                } else {
                    console.error("Enquiry Failed: ", result.message);
                    alert("Something went wrong with submission. Please check your inputs.");
                }

            } catch (error) {
                console.error("Error connecting to server:", error);
                alert("Could not connect to the server. Please check if your Python Flask backend is running!");
            }
        });
    }

    // Modal dismiss controls
    if (dismissBtn) {
        dismissBtn.addEventListener('click', () => {
            modal.classList.remove('active');
        });
    }

    if (modal) {
        modal.addEventListener('click', (event) => {
            if (event.target === modal) {
                modal.classList.remove('active');
            }
        });
    }

    // --- 7. SCHOLARSHIP FORM SUBMISSION & ADMIT SLIP GENERATOR ---
    // Sends scholarship requests to Python, retrieves a roll number, and displays the slip
    const scholarshipForm = document.getElementById('scholarshipForm');
    const scholarshipSlipModal = document.getElementById('scholarshipSlipModal');
    const printSlipBtn = document.getElementById('printSlipBtn');
    const closeSlipBtn = document.getElementById('closeSlipBtn');

    if (scholarshipForm) {
        scholarshipForm.addEventListener('submit', async (event) => {
            event.preventDefault(); // Prevents standard page refreshes

            // Gather all candidate variables
            const nameVal = document.getElementById('scholName').value;
            const residenceVal = document.getElementById('scholResidence').value;
            const phoneVal = document.getElementById('scholPhone').value;
            const schoolVal = document.getElementById('scholSchool').value;
            const heardFromVal = document.getElementById('scholHeard').value;

            try {
                // Post data payload to Python server API
                const response = await fetch('/register-scholarship', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        name: nameVal,
                        residence: residenceVal,
                        phone: phoneVal,
                        school: schoolVal,
                        heardFrom: heardFromVal
                    })
                });

                const result = await response.json();

                if (response.ok && result.status === 'success') {
                    // Populate Admit Slip fields inside index.html dynamically
                    document.getElementById('slipRollNo').textContent = result.student.roll_number;
                    document.getElementById('slipName').textContent = result.student.name;
                    document.getElementById('slipSchool').textContent = result.student.school;
                    document.getElementById('slipResidence').textContent = result.student.residence;

                    // Reveal printable Admit Card overlay
                    scholarshipSlipModal.classList.add('active');
                    scholarshipForm.reset();
                } else {
                    alert("Registration Error: " + result.message);
                }

            } catch (error) {
                console.error("Connection error:", error);
                alert("Could not connect to the Python backend server. Please make sure it is running!");
            }
        });
    }

    // Print action triggers native browser print dialog
    if (printSlipBtn) {
        printSlipBtn.addEventListener('click', () => {
            window.print(); 
        });
    }

    if (closeSlipBtn) {
        closeSlipBtn.addEventListener('click', () => {
            scholarshipSlipModal.classList.remove('active');
        });
    }

    if (scholarshipSlipModal) {
        scholarshipSlipModal.addEventListener('click', (event) => {
            if (event.target === scholarshipSlipModal) {
                scholarshipSlipModal.classList.remove('active');
            }
        });
    }

    // --- 8. DYNAMIC CHATBOT "PARA" CONVERSATION SYSTEM ---
    // A fully functional interactive chatbot featuring typing indicators and responsive answers
    const launcher = document.getElementById('paraBotLauncher');
    const chatWindow = document.getElementById('paraBotWindow');
    const closeBotBtn = document.getElementById('paraBotClose');
    const messagesContainer = document.getElementById('paraBotMessages');
    const botInput = document.getElementById('paraBotInput');
    const sendBotBtn = document.getElementById('paraBotSend');
    const chipButtons = document.querySelectorAll('.para-chip');

    if (launcher) {
        launcher.addEventListener('click', () => {
            chatWindow.classList.add('active');
            launcher.style.display = 'none'; // Smoothly hide circular launcher when open
            
            // Greets the user naturally if the chat starts completely blank
            if (messagesContainer.children.length === 0) {
                showTypingThenReply("Hi! I'm **Para**, your virtual assistant. 😊 How can I help you today?");
            }
        });
    }

    if (closeBotBtn) {
        closeBotBtn.addEventListener('click', () => {
            chatWindow.classList.remove('active');
            setTimeout(() => {
                launcher.style.display = 'flex'; // Bring launcher launcher icon back smoothly
            }, 200);
        });
    }

    // Simulates an elegant typing delay indicator for "Para"
    function showTypingThenReply(replyText) {
        // Build typing dots visual container
        const typingBubble = document.createElement('div');
        typingBubble.className = 'para-msg bot typing-msg';
        typingBubble.innerHTML = `
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        messagesContainer.appendChild(typingBubble);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Swap out dots with the actual text response after 1.1s
        setTimeout(() => {
            typingBubble.remove();
            
            const messageBubble = document.createElement('div');
            messageBubble.className = 'para-msg bot';
            // Render basic inline highlights nicely
            messageBubble.innerHTML = replyText;
            messagesContainer.appendChild(messageBubble);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 1100);
    }

    // Handles user search queries and returns custom answers matching your institute info
    function handleUserMessage(message) {
        const userBubble = document.createElement('div');
        userBubble.className = 'para-msg user';
        userBubble.textContent = message;
        messagesContainer.appendChild(userBubble);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        const cleanMessage = message.toLowerCase().trim();

        // Conversational Database matching Paraworld's real data
        let reply = "I didn't quite catch that. Could you ask about our **teachers**, **scholarship**, or **classes**? Or select one of the quick options below! 👇";

        if (cleanMessage.includes('hello') || cleanMessage.includes('hi') || cleanMessage.includes('hey')) {
            reply = "Hello! Hope you are having a fantastic day. How can I help you choose your dream course today? 🎓";
        } 
        else if (cleanMessage.includes('teacher') || cleanMessage.includes('faculty') || cleanMessage.includes('sir') || cleanMessage.includes('staff')) {
            reply = "We have an incredible faculty of 13+ experienced mentors! 👨‍🏫<br><br>" +
                    "• **Physics:** Sajad Sir & Aqib Sir<br>" +
                    "• **Chemistry:** Owais Sir & Yasir Sir<br>" +
                    "• **Mathematics:** Sajad Sir<br>" +
                    "• **Botany & Zoology:** Tariq Sir & Basharat Sir<br>" +
                    "• **Humanities:** Mashooq Sir & Ayaan Sir<br>" +
                    "• **Languages:** Khalid Sir (Urdu) & Abaas Sir (English)<br>" +
                    "• **MD:** Mansa Umer";
        } 
        else if (cleanMessage.includes('scholarship') || cleanMessage.includes('apply') || cleanMessage.includes('test') || cleanMessage.includes('exam')) {
            reply = "Securing a scholarship is simple! 🏆 Just scroll up to our **Scholarship Entry Form**, fill in your school, contact details, and village. You'll instantly get a printable Roll Number Slip with a seat reserved!";
        } 
        else if (cleanMessage.includes('location') || cleanMessage.includes('where') || cleanMessage.includes('shopian') || cleanMessage.includes('address') || cleanMessage.includes('locate')) {
            reply = "We are located at: **Therian, near Government Degree College Road, Shopian**. It's safe, central, and very easy to walk to! 📍";
        } 
        else if (cleanMessage.includes('subject') || cleanMessage.includes('courses') || cleanMessage.includes('classes') || cleanMessage.includes('standard') || cleanMessage.includes('taught')) {
            reply = "We offer premium classes for **10th, 11th, and 12th standard** board exams, alongside special competitive NEET/JEE prep batches in **Physics, Chemistry, Botany, Zoology, Mathematics, English, Urdu, History, Political Science, and Geography**!";
        }
        else if (cleanMessage.includes('winter') || cleanMessage.includes('heating') || cleanMessage.includes('cold')) {
            reply = "Don't worry about winter! ❄️ We provide excellent heating systems in all our classrooms to keep you warm, comfortable, and focused on your studies all year round.";
        }
        else if (cleanMessage.includes('phone') || cleanMessage.includes('number') || cleanMessage.includes('contact') || cleanMessage.includes('call') || cleanMessage.includes('md')) {
            reply = "You can call our clerk, **Murtaza Sir**, or our admissions team during office hours (Mon-Sat, 9 AM - 5 PM) at our campus on GDC Road, Shopian! 📞";
        }

        showTypingThenReply(reply);
    }

    // Input area send listeners
    if (sendBotBtn) {
        sendBotBtn.addEventListener('click', () => {
            const text = botInput.value;
            if (text.trim() !== '') {
                handleUserMessage(text);
                botInput.value = '';
            }
        });
    }

    if (botInput) {
        botInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const text = botInput.value;
                if (text.trim() !== '') {
                    handleUserMessage(text);
                    botInput.value = '';
                }
            }
        });
    }

    // Chip quick selection actions
    chipButtons.forEach(chip => {
        chip.addEventListener('click', () => {
            const question = chip.getAttribute('data-question');
            handleUserMessage(question);
        });
    });

});