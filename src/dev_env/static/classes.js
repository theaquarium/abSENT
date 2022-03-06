const textTemplate = document.querySelector('#text');
const updateTemplate = document.querySelector('#update');
const numberCardTemplate = document.querySelector('#number-card');

let updateDeleteListener = () => {};
let numberCardClickListener = () => {};
let conversationDeleteListener = () => {};

class User {
    constructor({ id = uuidv4(), name }) {
        this.id = id;
        this.name = name;
    }

    toObject() {
        return {
            id: this.id,
            name: this.name
        }
    }
}

class Update {
    constructor({id = uuidv4(), uid, name, body, formattedDate}) {
        this.id = id;
        this.body = body;
        this.date = formattedDate;

        this.user = new User({ id: uid, name });

        this.element = updateTemplate.content.firstElementChild.cloneNode(true);
        this.element.querySelector('.update-name').innerHTML = this.user.name;
        this.element.querySelector('.update-date').innerHTML = `(${this.date.dateString} ${this.date.timeString})`;
        this.element.querySelector('.update-content').appendChild(Update.bodyToTable(this.body));
        this.element.querySelector('.update-delete').addEventListener('click', () => {
            // handle deleting in here so you don't have to iterate over the update cards
            this.element.remove();
            updateDeleteListener(this.id);
        });
    }

    static bodyToTable(body) {
        let result = document.createElement('table');

        const rows = body.split('\n\n\n');
        rows.forEach((row) => {
            const rowElement = document.createElement('tr');
            const cols = row.split('\n');
            cols.forEach((cell) => {
                const cellElement = document.createElement('td');
                cellElement.innerText = cell;
                rowElement.appendChild(cellElement);
            });
            result.appendChild(rowElement);
        })

        return result;
    }

    getHTML() {
        return this.element;
    }

    toObject() {
        return {
            id: this.id,
            user: this.user.toObject(),
            body: this.body,
            date: this.date.date.toTime(),
        }
    }
}

class Conversation {
    constructor({number, texts = []}) {
        this.number = number;
        this.texts = texts;
        this.numUnread = 0;
        this.isActive = false;

        this.cardElement = numberCardTemplate.content.firstElementChild.cloneNode(true);
        this.cardElement.querySelector('.sms-number-card-text').innerText = this.number;
        this.cardElement.addEventListener('click', numberCardClickListener.bind(this, this.number));
        this.cardElement.querySelector('.sms-number-card-delete').addEventListener('click', (e) => {
            if (!confirm('Are you sure you want to delete this conversation?')) return;

            e.stopPropagation();

            this.cardElement.remove();
            conversationDeleteListener(this.number);
        });
    }

    rerender() {
        if (this.isActive) {
            this.cardElement.classList.add('is-active-number');
        } else {
            this.cardElement.classList.remove('is-active-number');
        }
        if (this.numUnread > 0) {
            this.cardElement.classList.add('is-unread-number');
            this.cardElement.querySelector('.sms-number-card-text').innerText = `${this.number} (${this.numUnread} new)`;
        } else {
            this.cardElement.classList.remove('is-unread-number');
            this.cardElement.querySelector('.sms-number-card-text').innerText = this.number;
        }
    }

    getHTMLCard() {
        return this.cardElement;
    }

    setActive() {
        this.numUnread = 0;
        this.isActive = true;
        this.rerender();
    }

    setInactive() {
        this.isActive = false;
        this.rerender();
    }

    addText(text) {
        this.texts.push(text);
        if (!this.isActive) {
            this.numUnread += 1;
        }
        this.rerender();
    }

    toObject() {
        const textsAsObjects = this.texts.map((text) => text.toObject());
        return {
            number: this.number,
            texts: textsAsObjects,
        }
    }
}

class SMSText {
    constructor({isUser, body}) {
        this.isUser = isUser;
        this.body = body;

        this.element = textTemplate.content.firstElementChild.cloneNode(true);
        this.element.classList.add('sms-text-from-' + (this.isUser ? 'user' : 'absent'));
        this.element.innerHTML = this.body.replaceAll('\\n', '<br />');
    }

    getHTML() {
        return this.element;
    }

    toObject() {
        return {
            isUser: this.isUser,
            body: this.body,
        }
    }
}
