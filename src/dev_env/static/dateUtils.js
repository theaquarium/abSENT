const dateFormatter = new Intl.DateTimeFormat('en-US' , {
    hour12: false,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
});
const days = ['MON', 'TUES', 'WEDS', 'THURS', 'FRI', 'SAT', 'SUN'];

const parseDate = (rawString) => {
    const now = formatDate(new Date());

    const dateParts = rawString.split(' ');
    const dateString = dateParts.shift().trim();
    const timeString = dateParts.join(' ').trim();

    // shift and join is used here to get everything before first space as DATE and the rest as TIME
    const dateOnly = new Date(dateString);
    const timeOnly = new Date(`${now.dateString} ${timeString}`);

    const updateDate = now.date;

    // if either is valid, set it to that
    // if the date string is empty, js marks it as invalid
    if (!isNaN(dateOnly)) {
        updateDate.setFullYear(
            dateOnly.getFullYear(),
            dateOnly.getMonth(),
            dateOnly.getDate(),
        );
    }
    // date is invalid if all three are 0 or if any are NaN
    if (timeString !== '' && (!isNaN(timeOnly.getHours())
        && !isNaN(timeOnly.getMinutes())
        && !isNaN(timeOnly.getSeconds()))) {
        updateDate.setHours(timeOnly.getHours());
        updateDate.setMinutes(timeOnly.getMinutes());
        updateDate.setSeconds(timeOnly.getSeconds());
    }

    return updateDate;
};

const formatDate = (date) => {
    const dateParts = dateFormatter.formatToParts(date);

    const dateString = dateParts.slice(0, 5).reduce((acc, {_, value}) => acc + value, '');
    const timeString = dateParts.slice(6).reduce((acc, {_, value}) => acc + value, '');

    return {
        date,
        dateString,
        timeString,
        dow: days[date.getDay()],
    }
}
