## 📋 Business Scenario

Our company needs a system to manage long-term customer subscriptions for high-value company resources. These resources could be physical assets (like heavy machinery, vehicles, or specialized hardware) or human resources (like dedicated consultants or engineers).

You need to build a complete system from scratch that handles these subscriptions, calculates pricing, prevents double-booking, and automates notifications. **Note: You cannot use the native Odoo Enterprise Subscription app for this.**

---

## 💼 Functional Requirements

### 1. Subscription & Resource Management

The system must track active customer subscriptions.
Each subscription must contain a customer, an assigned internal Account Manager, start/end dates, and a list of specific resources being subscribed to.
**Flexibility Rule:** A single subscription line should be flexible enough to link to either a standard product in our catalog or a specific, unique company asset.

### 2. Automated Numbering & Strict Validation Rules

**Document ID:** Every time a new subscription is created, the system must automatically generate a unique, sequential ID (e.g., SUB/2026/00001).
**Locking Approved Contracts:** Once a subscription is moved to the **"Approved"** stage, the pricing and the customer name must become locked. Only a user with **Manager** privileges should be allowed to modify an approved contract.
**Deletion Rules:** Users should never be allowed to delete a subscription unless it is still in the **"Draft"** stage. If they try to delete an active or approved subscription, the system must block them and display a clear warning message.
**Dynamic Search:** When searching for subscriptions in dropdown menus, the system must display them as [Sequence Number] - Customer Name for easy identification.

### 3. Pricing & Booking Logic

**Smart Discounts:** The system must automatically calculate the total cost of the subscription based on the items added. If the total calculation exceeds $10,000, a **10% volume discount** must automatically apply to the grand total.
**Customer Defaults:** When a customer is selected for a subscription, their default payment terms and delivery addresses must auto-populate instantly, but the salesperson should be allowed to change them if needed.
**Double-Booking Guardrail:** The system must strictly prevent a resource from being booked for overlapping dates. If "Resource A" is already subscribed by Customer X from Jan 1st to Jan 15th, the system must block any employee from subscribing "Resource A" to Customer Y on Jan 10th.

### 4. User Interface & Dashboards

**Pipeline Progress:** The subscription screen needs a visual progress bar showing the stages: Draft ➡️ Under Review ➡️ Approved ➡️ Expired ➡️ Cancelled.
**Management Dashboard:** Provide a card-based (Kanban) dashboard grouped by stage. If a subscription is getting close to its expiration date, it should visually stand out (e.g., color-coded red or yellow).
**Customer History:** On the standard Customer/Contact screen, add a visual counter/button showing how many active subscriptions that customer has. Clicking it should instantly take the employee to a list of just those subscriptions.
**Printable Summary:** Create a clean, professional, printable PDF document summarizing the subscription details and costs that can be sent to the client.

### 5. Security & Team Permissions

There must be two types of users in this system: **Subscription Users** and **Subscription Managers**.
**Data Privacy:** A standard Subscription User should only be able to see and edit subscriptions where they are explicitly assigned as the "Account Manager". They must not see other employees' clients.
**Global Access:** Subscription Managers must be able to see, edit, and manage all subscriptions across the entire company.

### 6. Automated Expiry & Email Notifications

The system must check itself automatically every night.
If a subscription reaches its end date today, the system must automatically change its status to Expired without any human intervention.
At the exact moment it expires, the system must automatically send a pre-formatted email notification to both the customer and their Account Manager.