document.addEventListener("DOMContentLoaded", () => {
    const App = {
        API_BASE: "http://127.0.0.1:8000/api",
        activeGoalId: null,
        elements: {
            goalForm: document.getElementById("goal-form"),
            goalInput: document.getElementById("goal-input"),
            startDateInput: document.getElementById("start-date"),
            submitBtn: document.getElementById("submit-btn"),
            submitBtnText: document.querySelector("#submit-btn .btn-text"),
            submitBtnSpinner: document.querySelector("#submit-btn .spinner"),
            goalsList: document.getElementById("goals-list"),
            goalDetails: document.getElementById("goal-details"),
        },
        init() {
            this.elements.goalForm.addEventListener("submit", this.handleCreateGoal.bind(this));
            this.setDefaultStartDate();
            this.fetchAndRenderGoals();
            this.renderDetailsPlaceholder("Select a goal to see its action plan.");
        },
        setDefaultStartDate() {
            this.elements.startDateInput.value = new Date().toISOString().split('T')[0];
        },
        async fetchApi(endpoint, options = {}) {
            try {
                const response = await fetch(`${this.API_BASE}${endpoint}`, options);
                if (!response.ok) {
                    const errorData = await response.json();
                    let errorMessage = "An API error occurred.";
                    if (errorData.detail && Array.isArray(errorData.detail)) {
                        errorMessage = errorData.detail.map(err => `${err.msg} (in ${err.loc[1]})`).join('\n');
                    } else if (errorData.detail) {
                        errorMessage = errorData.detail;
                    }
                    throw new Error(errorMessage);
                }
                return response.status === 204 ? null : response.json();
            } catch (error) {
                console.error("API Error Details:", error);
                alert(`Error:\n${error.message}`);
                return null;
            }
        },
        setLoading(isLoading) {
            this.elements.submitBtn.disabled = isLoading;
            this.elements.submitBtnText.classList.toggle("hidden", isLoading);
            this.elements.submitBtnSpinner.classList.toggle("hidden", !isLoading);
        },
        renderDetailsPlaceholder(message) {
            this.elements.goalDetails.innerHTML = `<div class="placeholder">${message}</div>`;
        },
        renderGoalsSkeleton() {
            this.elements.goalsList.innerHTML = `
                <div class="skeleton skeleton-item"></div>
                <div class="skeleton skeleton-item"></div>
                <div class="skeleton skeleton-item"></div>
            `;
        },
        async fetchAndRenderGoals() {
            this.renderGoalsSkeleton();
            const goals = await this.fetchApi("/goals");
            this.elements.goalsList.innerHTML = "";

            if (goals && goals.length > 0) {
                goals.forEach(goal => {
                    const div = document.createElement("div");
                    div.className = "goal-item fade-in";
                    div.dataset.goalId = goal.id;
                    div.innerHTML = `
                        <span>${goal.title}</span>
                        <div class="progress-bar">
                            <div class="progress-bar-inner" style="width: ${Math.round(goal.completion * 100)}%;"></div>
                        </div>
                    `;
                    div.onclick = () => this.showGoal(goal.id);
                    this.elements.goalsList.appendChild(div);
                });
            } else {
                this.elements.goalsList.innerHTML = `<div class="placeholder">No goals yet. Create one above!</div>`;
            }
            this.updateActiveGoalStyle();
        },
        async showGoal(goalId) {
            this.activeGoalId = goalId;
            this.updateActiveGoalStyle();
            this.renderDetailsPlaceholder("Loading tasks...");
            const goal = await this.fetchApi(`/goals/${goalId}`);
            if (goal) {
                this.renderGoalDetails(goal);
            }
        },
        renderGoalDetails(goal) {
            const formatDate = (dateString) => {
                return new Date(dateString).toLocaleDateString(undefined, { month: 'short', day: 'numeric', timeZone: 'UTC' });
            };

            let phasesHtml = "";
            for (const phaseTitle in goal.phases) {
                const tasks = goal.phases[phaseTitle];
                phasesHtml += `
                    <div class="phase-block fade-in">
                        <h4 class="phase-title">${phaseTitle}</h4>
                        <ul class="task-list">
                            ${tasks.map(task => `
                                <li>
                                    <input type="checkbox" id="task-${task.id}" ${task.completed ? "checked" : ""} 
                                           onchange="App.toggleTask(${task.id}, ${goal.id})"/>
                                    <label for="task-${task.id}">${task.title}</label>
                                    <span class="task-due-date">Due: ${formatDate(task.due_date)}</span>
                                </li>
                                <p class="task-description">${task.description}</p>
                            `).join("")}
                        </ul>
                    </div>
                `;
            }

            if (Object.keys(goal.phases).length === 0) {
                 phasesHtml = `<div class="placeholder">No tasks for this goal. Looks like you're all done!</div>`;
            }

            this.elements.goalDetails.innerHTML = `
                <div>
                    ${phasesHtml}
                    <button class="delete-btn" onclick="App.deleteGoal(${goal.id})">
                        <svg><use href="#icon-trash"></use></svg>
                        Delete Goal
                    </button>
                </div>
            `;
        },
        updateActiveGoalStyle() {
            document.querySelectorAll('.goal-item').forEach(item => {
                item.classList.toggle('active', item.dataset.goalId == this.activeGoalId);
            });
        },
        async handleCreateGoal(e) {
            e.preventDefault();
            const title = this.elements.goalInput.value.trim();
            const startDate = this.elements.startDateInput.value;

            if (!title || !startDate) {
                this.showFloatingMessage("Please provide both a goal title and a start date.", "error");
                return;
            }

            this.setLoading(true);
            this.renderDetailsPlaceholder(`🤖 Generating an intelligent plan for "${title}"...`);

            try {
                const createdGoal = await this.fetchApi("/goals", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ title, start_date: startDate })
                });

                if (createdGoal) {
                    this.elements.goalInput.value = "";
                    await this.fetchAndRenderGoals();
                    this.activeGoalId = createdGoal.id;
                    localStorage.setItem('activeGoalId', this.activeGoalId);
                    this.showGoal(this.activeGoalId);
                    this.showFloatingMessage("Plan created successfully!", "success");
                } else {
                    this.showFloatingMessage("The AI could not create a meaningful plan for this goal. Please try a more specific or different goal.", "error");

                }
            } finally {
                this.setLoading(false);
            }
        },
        showFloatingMessage(message, type) {
            const messageDiv = document.createElement("div");
            messageDiv.className = `floating-message ${type}`;
            messageDiv.textContent = message;
            document.body.appendChild(messageDiv);

            setTimeout(() => {
                messageDiv.classList.add("fade-out");
                messageDiv.addEventListener("transitionend", () => messageDiv.remove());
            }, 3000);
        },
        async toggleTask(taskId, goalId) {
            await this.fetchApi(`/tasks/${taskId}/toggle`, { method: "PATCH" });
            this.showGoal(goalId);
            this.fetchAndRenderGoals();
        },
        async deleteGoal(goalId) {
            if (confirm("Are you sure you want to delete this goal?")) {
                await this.fetchApi(`/goals/${goalId}`, { method: "DELETE" });
                this.activeGoalId = null;
                this.fetchAndRenderGoals();
                this.renderDetailsPlaceholder("Select a goal to see its action plan.");
            }
        },
    };

    window.App = App;
    App.init();
});