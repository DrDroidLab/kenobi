import React from 'react';
import styles from "./index.module.css";

function Card(props) {
    const { url = null, title, desc, id } = props;
    return (
        <div className={styles['cardContainer']} key={id}>
            <div className={styles['card']} >
                <img src={url} alt="alternatetext" className={styles['cardImage']}/>
                <h1 className={styles['cardTitle']}>{title}</h1>
                <h6 className={styles['cardDesc']}>{desc}</h6>
            </div>
        </div>
    );
}

export default Card;