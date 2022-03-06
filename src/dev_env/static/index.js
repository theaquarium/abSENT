// websocket stuff
let ws = null;

const sendWsMessage = (message) => {
    const jsonString = JSON.stringify(message);
    ws.send(jsonString);
}

const storageController = new StorageController();

const loadedResult = storageController.load();

/* {
 *     phone number: [{
 *         id: uuid,
 *         fromUser: bool,
 *         body: string,
 *     }],
 * }
 */
let conversations = loadedResult.conversations;
let activeConversation = '';

/* [
 *     {
 *         id: uuid,
 *         name: string,
 *         body: string,
 *     },
 * ]
 */
let southUpdateFeed = loadedResult.southUpdateFeed;
let northUpdateFeed = loadedResult.northUpdateFeed;
let currentFeed = 0;

let frozenDate = loadedResult.frozenDate;


// panels
let activePanel = 0;
const schoologyPanel = document.querySelector('.schoology-sim');
const smsPanel = document.querySelector('.sms-sim');
const dividerPanel = document.querySelector('.divider');

dividerPanel.addEventListener('click', () => {
    if (activePanel !== 0) {
        schoologyPanel.classList.remove('is-bigger');
        smsPanel.classList.add('is-bigger');
        activePanel = 0;
    } else if (activePanel !== 1) {
        smsPanel.classList.remove('is-bigger');
        schoologyPanel.classList.add('is-bigger');
        activePanel = 1;
    }
});

// allow tabs in update textarea
// const updateTextarea = document.querySelector('#schoology-update-content');
// updateTextarea.addEventListener('keydown', (e) => {
//     if (e.key === 'Tab') {
//         e.preventDefault();
//         const start = updateTextarea.selectionStart;
//         const end = updateTextarea.selectionEnd;

//         // set textarea value to: text before caret + tab + text after caret
//         updateTextarea.value = updateTextarea.value.substring(0, start) + "    " + updateTextarea.value.substring(end);

//         // put caret at right position again
//         updateTextarea.selectionStart = start + 4;
//         updateTextarea.selectionEnd = start + 4;
//     }
// });

// sms simulator
const numbersList = document.querySelector('.sms-numbers-list');
const conversationHeader = document.querySelector('#sms-header-number');
const conversationArea = document.querySelector('.sms-conversation-texts');
const messageField = document.querySelector('#sms-input-field');

const numberCardClickListener = (number) => {
    activeConversation = number;
    const conversation = conversations[activeConversation];
    // mark all others as inactive
    Object.values(conversations).forEach((convo) => {
        if (convo.number === activeConversation) {
            convo.setActive();
        } else {
            convo.setInactive();
        }
    });

    conversationHeader.innerText = activeConversation;
    conversationArea.innerHTML = '';
    conversation.texts.forEach((text) => {
        conversationArea.appendChild(text.getHTML());
    });

    conversationArea.scrollTop = conversationArea.scrollHeight;
    messageField.focus();
};

const conversationDeleteListener = (number) => {
    delete conversations[number];
    if (Object.keys(conversations).length === 0) {
        numbersList.innerHTML = '<div class="add-number-message">Add a number to send a message to abSENT.</div>';
    }

    if (number === activeConversation) {
        conversationArea.innerHTML = '';
        conversationHeader.innerText = '__________';
    }

    // sendWsMessage({
    //     messageType: 'delete-conversation',
    //     number,
    // });

    storageController.saveConversations(conversations);
};

const createConversation = (number) => {
    const addNumberMessage = document.querySelector('.add-number-message');
    if (addNumberMessage) {
        addNumberMessage.remove();
    }
    const conversation = new Conversation({number})
    conversations[number] = conversation;
    numbersList.appendChild(conversation.getHTMLCard());

    setActiveConversation(number);
    storageController.saveConversations(conversations);
};

const addNumberButton = document.querySelector('#sms-add-number-button');
addNumberButton.addEventListener('click', () => {
    const randomPhoneNumber = Math.round(Math.random() * Math.pow(10, 10)).toString();
    const number = prompt('What phone number do you want to add?', `+1${randomPhoneNumber}`);
    if (number.length > 0) {
        if (conversations[number]) {
            alert('This conversation already exists.');
            return;
        }
        createConversation(number);
    } else {
        alert('Please enter a number');
    }
})

const sendText = () => {
    if (messageField.value.length > 0 && activeConversation.length > 0) {
        const newText = new SMSText({isUser: true, body: messageField.value});
        conversations[activeConversation].addText(newText);
        conversationArea.appendChild(newText.getHTML());
        conversationArea.scrollTop = conversationArea.scrollHeight;

        messageField.value = '';

        sendWsMessage({
            messageType: 'sms-from-user',
            number: activeConversation,
            body: newText.body,
        });

        storageController.saveConversations(conversations);
    }
};

const receiveText = (body, number) => {
    const newText = new SMSText({isUser: false, body: body});
    conversations[number].addText(newText);
    if (number === activeConversation) {
        conversationArea.appendChild(newText.getHTML());
        conversationArea.scrollTop = conversationArea.scrollHeight;
    }

    storageController.saveConversations(conversations);
};

const sendMessageButton = document.querySelector('#sms-input-send');
messageField.addEventListener('keyup', (e) => {
    if (e.key === 'Enter') {
        sendText();
    }
})
sendMessageButton.addEventListener('click', sendText)

// schoology sim

// table manager
let numCols = 5;

const addRowButton = document.querySelector('#schoology-add-row');
const removeRowButton = document.querySelector('#schoology-remove-row');
const addColButton = document.querySelector('#schoology-add-col');
const removeColButton = document.querySelector('#schoology-remove-col');
const clearButton = document.querySelector('#schoology-clear');

const updateContent = document.querySelector('.schoology-update-content');
const updateNameField = document.querySelector('#schoology-update-user');
const updateDateField = document.querySelector('#schoology-update-date');
const updateTimeField = document.querySelector('#schoology-update-time');

const getUpdateDate = () => {
    const date = parseDate(`${updateDateField.value} ${updateTimeField.value}`);
    const dateParts = formatDate(date);

    updateDateField.value = dateParts.dateString;
    updateTimeField.value = dateParts.timeString;

    return dateParts;
};

const addRow = () => {
    const rowElement = document.createElement('div');
    rowElement.classList.add('schoology-update-row');
    for (let i = 0; i < numCols; i += 1) {
        const cell = document.createElement('div');
        cell.classList.add('schoology-update-cell');
        const input = document.createElement('input');
        input.setAttribute('type', 'text');
        input.classList.add('schoology-update-cell-input');
        cell.appendChild(input);
        rowElement.appendChild(cell);
    }
    updateContent.appendChild(rowElement);
}
addRowButton.addEventListener('click', addRow);

removeRowButton.addEventListener('click', () => {
    if (updateContent.children.length > 0) {
        updateContent.lastElementChild.remove();
    }
});

const addCol = () => {
    numCols += 1;
    for (let i = 0; i < updateContent.children.length; i += 1) {
        const row = updateContent.children[i];
        
        const cell = document.createElement('div');
        cell.classList.add('schoology-update-cell');
        const input = document.createElement('input');
        input.setAttribute('type', 'text');
        input.classList.add('schoology-update-cell-input');
        cell.appendChild(input);
        row.appendChild(cell);
    }
};
addColButton.addEventListener('click', addCol);

removeColButton.addEventListener('click', () => {
    numCols = Math.max(0, numCols - 1);
    for (let i = 0; i < updateContent.children.length; i += 1) {
        const row = updateContent.children[i];
        
        if (row.children.length > 0) {
            row.lastElementChild.remove();
        }
    }
});

const clear = () => {
    numCols = 5;
    updateNameField.value = '';
    updateContent.innerHTML = '';
};

clearButton.addEventListener('click', () => {
    updateDateField.value = '';
    updateTimeField.value = '';
    clear();
    addRow();
});

// sample updates
const sampleSouthButton = document.querySelector('#schoology-sample-south');
const sampleNorthFriendButton = document.querySelector('#schoology-sample-north-friend');
const sampleNorthSpiritoButton = document.querySelector('#schoology-sample-north-spirito');

const sampleSouth = {
    name: 'Tracy Connolly',
    table: [
        [
            'MCFAKEHEAD',
            'KEVIN',
            'All Day',
            '%date%',
            'All blocks cancelled',
        ],
        [
            'STURGEON',
            'REBECCA',
            'Partial Day AM',
            '%date%',
            'A Block Cancelled',
        ],
        [
            'SPIDERMAN',
            'RYAN',
            'All Day',
            '%date%',
            'C, D, E, WIN Cancelled',
        ],
        [
            'Carton',
            'Sydney',
            'All Day',
            '%date%',
            'All blocks, Advisory cancelled, go to 6167',
        ],
        [
            'WEREWOLF',
            'NATHAN',
            'Partial Day PM',
            '%date%',
            'G Block cancelled, full moon today.',
        ],
        [
            'Tiramisu',
            'Alexa',
            'All Day',
            '%date%',
            'F Block Cooking cancelled.',
        ],
    ]
};

const sampleNorthFriend = {
    name: 'Casey Friend',
    table: [
        [
            'Position',
            'Last Name',
            'First Name',
            'Notes to Student',
            'Day',
            'DoW',
        ],
        [
            'Teacher Math',
            'MCFAKEHEAD',
            'KAYLA',
            'All blocks cancelled',
            'All Day',
            '%dow%',
        ],
        [
            'Teacher Soc Studies',
            'BILLIARDS',
            'WILLIAM',
            'C, D Block Cancelled',
            'Partial AM',
            '%dow%',
        ],
        [
            'Teacher Science',
            'CARBONOS',
            'TERRY',
            'A, B, F, G cancelled, I am here for Tiger',
            'All Day',
            '%dow%',
        ],
        [
            'Notary Public',
            'Darnay',
            'Charles',
            'All blocks cancelled, go to 105',
            'All Day',
            '%dow%',
        ],
        [
            'Counselor',
            'GHICK',
            'NICK',
            'WIN, Advisory cancelled',
            'Partial PM',
            '%dow%',
        ],
    ],
};

const sampleNorthSpirito = {
    name: 'Suzanne Spirito',
    table: [
        [
            'Position',
            'Last Name',
            'First Name',
            'Day',
            'DoW',
            'Notes to Student',
        ],
        [
            'Counselor',
            'Mint',
            'Teddy',
            'All Day',
            '%dow%',
            'All blocks cancelled',
        ],
        [
            'Teacher Math',
            'WRICKLE',
            'BILL',
            'Partial AM',
            '%dow%',
            'C, D Block Cancelled',
        ],
        [
            'Teacher Soc Studies',
            'OZONE',
            'ROB',
            'All Day',
            '%dow%',
            'A, B, F, G cancelled, I am here for Tiger',
        ],
        [
            'Teacher English',
            'Green',
            'Sarah',
            'All Day',
            '%dow%',
            'All blocks cancelled, go to 105',
        ],
        [
            'Counselor',
            'Tart',
            'Mort',
            'Partial PM',
            '%dow%',
            'WIN, Advisory cancelled',
        ],
    ],
};

const fillSample = (table) => {
    const updateDate = getUpdateDate();
    clear();

    const tableCols = table.table[0].length;
    numCols = tableCols;
    updateNameField.value = table.name;

    table.table.forEach((row) => {
        addRow();
        const cells = updateContent.lastChild.children;
        for (let i = 0; i < cells.length; i += 1) {
            const cell  = cells[i];

            let cellValue = row[i];
            if (cellValue === '%date%') {
                cellValue = updateDate.dateString;
            } else if (cellValue === '%dow%') {
                cellValue = updateDate.dow;
            }

            cell.firstElementChild.value = cellValue;
        }
    });
};

sampleSouthButton.addEventListener('click', fillSample.bind(null, sampleSouth));
sampleNorthFriendButton.addEventListener('click', fillSample.bind(null, sampleNorthFriend));
sampleNorthSpiritoButton.addEventListener('click', fillSample.bind(null, sampleNorthSpirito));

// delete update

// set listener
deleteUpdateListener = (id) => {
    if (currentFeed === 0) {
        southUpdateFeed = southUpdateFeed.filter((update) => update.id !== id);
        if (southUpdateFeed.length === 0) {
            updateFeedElement.innerHTML = '<p class="no-updates-message">No South updates yet!</p>';
        }
        storageController.saveSouthUpdates(southUpdateFeed);
    } else if (currentFeed === 1) {
        northUpdateFeed = northUpdateFeed.filter((update) => update.id !== id);
        if (northUpdateFeed.length === 0) {
            updateFeedElement.innerHTML = '<p class="no-updates-message">No North updates yet!</p>';
        }
        storageController.saveNorthUpdates(northUpdateFeed);
    }
    sendWsMessage({
        messageType: 'delete-update',
        updateId: id,
    });
};


// feed manager

const southFeedButton = document.querySelector('#schoology-south-feed');
const northFeedButton = document.querySelector('#schoology-north-feed');
const updateFeedElement = document.querySelector('.schoology-feed');

southFeedButton.addEventListener('click', () => {
    currentFeed = 0;

    // change buttons
    southFeedButton.classList.add('is-active-feed');
    northFeedButton.classList.remove('is-active-feed');

    // load posts
    updateFeedElement.innerHTML = '';
    if (southUpdateFeed.length > 0) {
        southUpdateFeed.forEach((update) => {
            updateFeedElement.appendChild(update.getHTML());
        });
    } else {
        updateFeedElement.innerHTML = '<p class="no-updates-message">No South updates yet!</p>';
    }
});

northFeedButton.addEventListener('click', () => {
    currentFeed = 1;

    // change buttons
    northFeedButton.classList.add('is-active-feed');
    southFeedButton.classList.remove('is-active-feed');

    // load posts
    updateFeedElement.innerHTML = '';
    if (northUpdateFeed.length > 0) {
        northUpdateFeed.forEach((update) => {
            updateFeedElement.appendChild(update.getHTML());
        });
    } else {
        updateFeedElement.innerHTML = '<p class="no-updates-message">No North updates yet!</p>';
    }
    
});

// send update
const sendUpdateButton = document.querySelector('#schoology-send-update');
sendUpdateButton.addEventListener('click', () => {
    // must have name
    if (updateNameField.value.length === 0) {
        alert('Must include update name');
        return;
    };

    const updateDate = getUpdateDate();

    const noUpdatesMessage = document.querySelector('.no-updates-message');
    if (noUpdatesMessage) noUpdatesMessage.remove();

    let updateString = '';
    let containsContent = false;
    for (let i = 0; i < updateContent.children.length; i += 1) {
        const row = updateContent.children[i];

        if (i > 0) updateString += '\n\n\n';
        
        for (let j = 0; j < row.children.length; j += 1) {
            const cell = row.children[j].firstElementChild;

            if (j > 0) updateString += '\n';
            
            if (cell.value.length > 0) {
                containsContent = true;
                updateString += cell.value;
            } else {
                updateString += ' ';
            }
        }
    }

    // if it's an empty update, prompt for a plain text one
    if (!containsContent) {
        const textUpdate = prompt('Enter update text:');
        if (textUpdate.length === 0) {
            alert('Please enter update text.');
            return;
        }
        updateString = textUpdate;
    }

    const newUpdate = new Update({ name: updateNameField.value, body: updateString, formattedDate: updateDate });
    if (currentFeed === 0) {
        southUpdateFeed.unshift(newUpdate);

        sendWsMessage({
            messageType: 'south-update-posted',
            id: newUpdate.id,
            body: newUpdate.body,
            user: newUpdate.user,
            date: newUpdate.date.date.getTime(),
        });
        storageController.saveSouthUpdates(southUpdateFeed);
    } else if (currentFeed === 1) {
        northUpdateFeed.unshift(newUpdate);

        sendWsMessage({
            messageType: 'north-update-posted',
            id: newUpdate.id,
            body: newUpdate.body,
            user: newUpdate.user,
            date: newUpdate.date.date.getTime(),
        });
        storageController.saveNorthUpdates(northUpdateFeed);
    }

    updateFeedElement.prepend(newUpdate.getHTML());
});

// settings menu
const settingsMenu = document.querySelector('.settings-menu');
const settingsButton = document.querySelector('.settings-button');
const settingClearAll = document.querySelector('#setting-clear-all');
const settingClearConversations = document.querySelector('#setting-clear-conversations');
const settingClearUpdates = document.querySelector('#setting-clear-updates');
const settingAbsentDate = document.querySelector('#setting-absent-date');
const settingFreezeDate = document.querySelector('#setting-freeze-date');
const settingUnfreezeDate = document.querySelector('#setting-unfreeze-date');
const settingResetState = document.querySelector('#setting-reset-state');

let settingsOpen = false;
let settingsCloseTimeout = null;

const closeSettings = () => {
    settingsMenu.classList.add('is-closed-settings');
    settingsOpen = false;
    
    if (frozenDate != null) {
        settingAbsentDate.value = `${frozenDate.dateString} ${frozenDate.timeString}`;
    } else {
        settingAbsentDate.value = '';
    }
};

const openSettings = () => {
    settingsMenu.classList.remove('is-closed-settings');
    settingsOpen = true;
};

// settingsButton.addEventListener('mouseover', () => {
//     console.log('button mouseover, settings opened, new timeout')
//     toggleSettings();
//     settingsCloseTimeout = setTimeout(closeSettings, 1000);
// });

// automatically close setting on mouseout
settingsMenu.addEventListener('mouseout', () => {
    settingsCloseTimeout = setTimeout(closeSettings, 1000);
});

settingsMenu.addEventListener('mouseover', () => {
    clearTimeout(settingsCloseTimeout);
});

settingsButton.addEventListener('click', () => {
    if (settingsOpen) {
        closeSettings();
    } else {
        openSettings();
    }
});

const clearConversations = () => {
    conversations = {};
    numbersList.innerHTML = '<div class="add-number-message">Add a number to send a message to abSENT.</div>';
    conversationArea.innerHTML = '';
    conversationHeader.innerText = '__________';

    storageController.clearConversations();
}

const clearUpdates = () => {
    southUpdateFeed = [];
    northUpdateFeed = [];

    updateFeedElement.innerHTML = `<p class="no-updates-message">No ${currentFeed === 0 ? 'South' : 'North'} updates yet!</p>`;
    clear();

    storageController.clearNorthUpdates();
    storageController.clearSouthUpdates();
}

settingClearAll.addEventListener('click', () => {
    if (!confirm('Are you sure you would like to clear all data?')) return;

    sendWsMessage({
        messageType: 'clear-all',
    });
    clearConversations();
    clearUpdates();
    closeSettings();
});

settingClearConversations.addEventListener('click', () => {
    if (!confirm('Are you sure you would like to clear all conversations?')) return;

    // sendWsMessage({
    //     messageType: 'clear-conversations',
    // });
    clearConversations();
    closeSettings();
});

settingClearUpdates.addEventListener('click', () => {
    if (!confirm('Are you sure you would like to clear all updates?')) return;

    sendWsMessage({
        messageType: 'clear-updates',
    });
    clearUpdates();
    closeSettings();
});

settingFreezeDate.addEventListener('click', () => {
    frozenDate = formatDate(parseDate(settingAbsentDate.value));

    settingAbsentDate.value = `${frozenDate.dateString} ${frozenDate.timeString}`;

    alert(`Date frozen to ${frozenDate.dateString} ${frozenDate.timeString}.`);

    sendWsMessage({
        messageType: 'freeze-date',
        date: frozenDate.date.getTime(),
    });
    storageController.saveFrozenDate(frozenDate.date);
});

settingUnfreezeDate.addEventListener('click', () => {
    frozenDate = null;

    settingAbsentDate.value = '';

    alert(`Date unfrozen.`);

    sendWsMessage({
        messageType: 'unfreeze-date',
    });
    storageController.clearFrozenDate();
});

settingResetState.addEventListener('click', () => {
    if (!confirm('Are you sure you want to reset the state?')) return;

    sendWsMessage({
        messageType: 'reset-state',
    });
});

const connect = () => {
    ws = new WebSocket('ws://localhost:9000/ws');
    
    ws.onopen = () => {
        console.log('WebSocket connection open!');

        sendWsMessage({
            messageType: 'initial-load',
            ...StorageController.getFullStorageObject(loadedObject)
        });
    };

    ws.onclose = (e) => {
        console.log('Socket is closed. Reconnect will be attempted in 0.5 seconds.', e.reason);

        setTimeout(connect, 500);
    };
    
    ws.onerror = (err) => {
        console.error('Socket encountered error: ', err.message, 'Closing socket');
        ws.close();
    };

    // parse new texts from server
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('message received', data);
        if (data.messageType === 'sms-from-absent') {
            const number = data.number;
            const msgContent = data.body;
            if (!conversations[number]) {
                createConversation(number);
            }

            receiveText(msgContent, number);
        }
    };
};

connect();
