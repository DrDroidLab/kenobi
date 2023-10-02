import React, { useState, useEffect } from 'react';
import Card from '../CardComponent';
import { cardsData } from './IntegrationCardsData';
import Button from '../ButtonComponent';
import styles from './index.module.css';
import API from '../../API';
import Toast from '../../components/Toast';
import useToggle from '../../hooks/useToggle';
import { addToLocalArray, getLocalArray } from '../../utils/LocalStorageUtils';

function Cards({ includedIds, search }) {
  const [cards, setCards] = useState([]);

  const [validationError, setValidationError] = useState();
  const { isOpen, toggle } = useToggle();
  const { isOpen: IsError, toggle: toggleError } = useToggle();
  const [submitError, setSubmitError] = useState();

  const getConnector = API.useConnectorRequest();

  const updateCards = () => {
    let includedCardsData = cardsData.filter(data => includedIds.includes(data.id));
    includedCardsData = includedCardsData.filter(
      data =>
        data.desc.toLowerCase().indexOf(search.toLowerCase()) > -1 ||
        data.title.toLowerCase().indexOf(search.toLowerCase()) > -1
    );
    includedCardsData = includedCardsData.map((data, index) => ({ ...data, id: index }));

    for (let i = 0; i < includedCardsData.length; i++) {
      const connectorType = includedCardsData[i].enum;
      if (getLocalArray('requestedConnectors').includes(connectorType)) {
        includedCardsData[i].buttonType = 'requested';
        includedCardsData[i].buttonTitle = 'Requested';
      }
    }

    setCards(includedCardsData);
  };

  useEffect(() => {
    updateCards();
  }, []);

  useEffect(() => {
    updateCards();
  }, [search]);

  const connectorRequestHandler = dataId => {
    const updatedCards = cards.map(card => {
      if (card.id === dataId) {
        card.buttonType = 'requested';
        card.buttonTitle = 'Requested';
        return {
          ...card
        };
      }
      return card;
    });
    setCards(updatedCards);
    setValidationError(
      'Our team will shortly reach out to your will details on how to set this up.'
    );
    toggle();
    window.open(
      'https://calendly.com/siddarthjain/catchup-call-clone',
      '_blank',
      'noopener,noreferrer'
    );
  };

  const handleClick = data => {
    if (data.buttonType === 'link') {
      window.open(data.buttonLink, '_blank', 'noreferrer');
    } else {
      const createPayload = {
        connector_type: data.enum
      };

      const dataId = data.id;
      addToLocalArray('requestedConnectors', data.enum);

      getConnector(
        createPayload,
        response => {
          connectorRequestHandler(dataId);
        },
        err => {
          connectorRequestHandler(dataId);
        }
      );
    }
  };

  return (
    <>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 0fr)' }}>
        {cards.map(data => (
          <div key={data.id} className={styles['tabContainer']}>
            <Card
              key={data.id}
              url={data.url}
              title={data.title}
              desc={data.desc}
              buttonTitle={data.buttonTitle}
              buttonType={data.buttonType}
            />
            <Button
              key={`button-${data.id}`}
              buttonType={data.buttonType}
              label={data.buttonTitle}
              isLoading={data.isLoading}
              isDisabled={data.isDisabled}
              handleClick={() => handleClick(data)}
            />
          </div>
        ))}
      </div>
      <Toast
        open={!!isOpen}
        severity="info"
        message={validationError}
        handleClose={() => toggle()}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      />
      <Toast
        open={!!IsError}
        severity="error"
        message={submitError}
        handleClose={() => toggleError()}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      />
    </>
  );
}

export default Cards;
