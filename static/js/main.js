document.addEventListener('DOMContentLoaded', () => {

    // --- 1. DYNAMIC NAVIGATION COLOR SHIFT ON SCROLL ---
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 40) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // --- 2. MOBILE NAVIGATION DRAWER TOGGLE ---
    const hamburgerMenu = document.getElementById('hamburger-menu');
    const navDrawer = document.getElementById('nav-drawer');

    if (hamburgerMenu && navDrawer) {
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

        // Automatically close mobile menu when a link is clicked
        navDrawer.querySelectorAll('a').forEach(anchor => {
            anchor.addEventListener('click', () => {
                navDrawer.classList.remove('active');
                const bars = hamburgerMenu.querySelectorAll('div');
                bars[0].style.transform = 'none';
                bars[1].style.opacity = '1';
                bars[2].style.transform = 'none';
            });
        });
    }

    // --- 3. CLASSROOM SECTION - INTERACTIVE TAB DATA ENGINE ---
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
            text: "Shopian winters are cold, but our studies never pause. Our classroom environment stays warm and comfortable (equipped with modern heating and Hamam facilities) to make sure you never lose focus due to freezing weather."
        },
        boards: {
            icon: "🖊️",
            title: "Smart Teaching Boards",
            text: "Our physical whiteboards are clean, glare-free, and matched with colorful interactive illustrations from teachers to explain formulas and science mechanisms clearly."
        }
    };

    if (tabs && displayWindow) {
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Reset active tabs
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');

                // Pull corresponding data
                const key = tab.getAttribute('data-content');
                const data = contentMap[key];

                // Transition out old text
                displayWindow.style.opacity = '0';
                displayWindow.style.transform = 'scale(0.95)';

                setTimeout(() => {
                    // Insert new data
                    displayWindow.innerHTML = `
                        <span class="display-icon">${data.icon}</span>
                        <h3>${data.title}</h3>
                        <p>${data.text}</p>
                    `;
                    // Fade in new text
                    displayWindow.style.opacity = '1';
                    displayWindow.style.transform = 'scale(1)';
                }, 300);
            });
        });
    }

    // --- 4. INTERACTIVE FACULTY FILTERS ---
    const filterBtns = document.querySelectorAll('.filter-btn');
    const cards = document.querySelectorAll('.teacher-card');

    if (filterBtns && cards) {
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                // Update active category class
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
    }

    // --- 5. FAQ ACCORDION ENGINE ---
    const questions = document.querySelectorAll('.faq-question');
    if (questions) {
        questions.forEach(q => {
            q.addEventListener('click', () => {
                const item = q.parentElement;
                const isActive = item.classList.contains('active');

                // Close any other open FAQ items
                document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('active'));

                if (!isActive) {
                    item.classList.add('active');
                }
            });
        });
    }

    // --- 6. ADMISSION ENQUIRY SUBMISSION (GENERAL ENQUIRY) ---
    const enquiryForm = document.getElementById('enquiryForm');
    const modalWindow = document.getElementById('modalWindow');
    const dismissModalBtn = document.getElementById('dismissModalBtn');

    if (enquiryForm) {
        enquiryForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const studentName = document.getElementById('studentName').value;
            const studentPhone = document.getElementById('studentPhone').value;
            const gradeSelection = document.getElementById('gradeSelection').value;

            try {
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
                    modalWindow.classList.add('active');
                    enquiryForm.reset();
                } else {
                    alert("Something went wrong with submission. Please check your inputs.");
                }

            } catch (error) {
                alert("Could not connect to the server. Please check if your Python Flask backend is running!");
            }
        });
    }

    if (dismissModalBtn) {
        dismissModalBtn.addEventListener('click', () => {
            modalWindow.classList.remove('active');
        });
    }

    // --- 7. SCHOLARSHIP FORM SUBMISSION & ADMIT SLIP GENERATOR ---
    const scholarshipForm = document.getElementById('scholarshipForm');
    const scholarshipSlipModal = document.getElementById('scholarshipSlipModal');
    const printSlipBtn = document.getElementById('printSlipBtn');
    const closeSlipBtn = document.getElementById('closeSlipBtn');

    if (scholarshipForm) {
        scholarshipForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const nameVal = document.getElementById('scholName').value;
            const emailVal = document.getElementById('scholEmail').value;
            const residenceVal = document.getElementById('scholResidence').value;
            const phoneVal = document.getElementById('scholPhone').value;
            const schoolVal = document.getElementById('scholSchool').value;
            const currentClassVal = document.getElementById('scholCurrentClass').value;
            const promotingClassVal = document.getElementById('scholPromotingClass').value;
            const heardFromVal = document.getElementById('scholHeard').value;

            try {
                const response = await fetch('/register-scholarship', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        name: nameVal,
                        email: emailVal,
                        residence: residenceVal,
                        phone: phoneVal,
                        school: schoolVal,
                        currentClass: currentClassVal,
                        promotingClass: promotingClassVal,
                        heardFrom: heardFromVal
                    })
                });

                const result = await response.json();

                if (response.ok && result.status === 'success') {
                    // Populate Admit Slip fields inside index.html dynamically
                    document.getElementById('slipRollNo').textContent = result.student.roll_number;
                    document.getElementById('slipName').textContent = result.student.name;
                    document.getElementById('slipEmail').textContent = result.student.email;
                    document.getElementById('slipCurrentClass').textContent = result.student.current_class;
                    document.getElementById('slipPromotingClass').textContent = result.student.promoting_class;
                    document.getElementById('slipSchool').textContent = result.student.school;
                    document.getElementById('slipResidence').textContent = result.student.residence;

                    // Reveal printable Admit Card overlay
                    scholarshipSlipModal.classList.add('active');
                    scholarshipForm.reset();
                } else {
                    alert("Registration Error: " + result.message);
                }

            } catch (error) {
                alert("Could not connect to the Python backend server!");
            }
        });
    }

    if (printSlipBtn) { printSlipBtn.addEventListener('click', () => { window.print(); }); }
    if (closeSlipBtn) { closeSlipBtn.addEventListener('click', () => { scholarshipSlipModal.classList.remove('active'); }); }

    // --- 8. MINI GEMINI AI CHATBOT INTEGRATION ---
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
            launcher.style.display = 'none';
            if (messagesContainer.children.length === 0) {
                // Initial greeting without calling API
                const greeting = "Hi! I am **Mini Gemini**, your AI tutor for Paraworld Educations. I can help you solve math problems, explain science concepts, or tell you about our institute. How can I help you today? 😊";
                displayBotMessage(greeting);
            }
        });
    }

    if (closeBotBtn) {
        closeBotBtn.addEventListener('click', () => {
            chatWindow.classList.remove('active');
            setTimeout(() => { launcher.style.display = 'flex'; }, 200);
        });
    }

    function formatAIMessage(text) {
        // Convert basic markdown formatting from Gemini to HTML
        let formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>'); // Bold
        formattedText = formattedText.replace(/\*(.*?)\*/g, '<em>$1</em>');       // Italics
        formattedText = formattedText.replace(/\n/g, '<br>');                     // Line breaks
        return formattedText;
    }

    function displayBotMessage(text) {
        const messageBubble = document.createElement('div');
        messageBubble.className = 'para-msg bot';
        messageBubble.innerHTML = formatAIMessage(text);
        messagesContainer.appendChild(messageBubble);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    async function handleUserMessage(message) {
        // 1. Display the user's message
        const userBubble = document.createElement('div');
        userBubble.className = 'para-msg user';
        userBubble.textContent = message;
        messagesContainer.appendChild(userBubble);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // 2. Show the animated typing dots
        const typingBubble = document.createElement('div');
        typingBubble.className = 'para-msg bot typing-msg';
        typingBubble.innerHTML = `<div class="typing-dots"><span></span><span></span><span></span></div>`;
        messagesContainer.appendChild(typingBubble);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        try {
            // 3. Send the message securely to our Python server (which talks to Google)
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });

            const result = await response.json();

            // 4. Remove typing dots
            typingBubble.remove();

            // 5. Display Mini Gemini's brilliant response!
            if (response.ok && result.status === 'success') {
                displayBotMessage(result.response);
            } else {
                displayBotMessage("Oops! My AI brain is currently offline. " + (result.message || "Try again later."));
            }

        } catch (error) {
            typingBubble.remove();
            displayBotMessage("I am having trouble connecting to the network! Please check your internet connection.");
        }
    }

    if (sendBotBtn) {
        sendBotBtn.addEventListener('click', () => {
            const text = botInput.value;
            if (text.trim() !== '') { handleUserMessage(text); botInput.value = ''; }
        });
    }

    if (botInput) {
        botInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const text = botInput.value;
                if (text.trim() !== '') { handleUserMessage(text); botInput.value = ''; }
            }
        });
    }

    // Allow quick-action chips to send messages to the AI
    chipButtons.forEach(chip => {
        chip.addEventListener('click', () => {
            handleUserMessage(chip.getAttribute('data-question'));
        });
    });
});
