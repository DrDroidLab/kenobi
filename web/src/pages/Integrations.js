import React from 'react';
import { Link } from 'react-router-dom';
import backImage from '../data/integrations.png';
import '../css/comingSoon.css';
import Heading from '../components/Heading';

function Integrations() {
  return (
    <>
      <Heading heading={'Integrations'} />
      <div>
        <div
          className="comingSoon-container"
          style={{
            backgroundImage: `url(${backImage})`
          }}
        ></div>
        <div className="comingSoon-card">
          <div className="text-3xl text-black-600 mb-3 text-center">Coming Soon</div>
          <Link to="/">
            <button className="text-sm bg-violet-600 hover:bg-violet-700 px-4 py-2  rounded-lg">
              Go to Home
            </button>
          </Link>
        </div>
      </div>
    </>
  );
}

export default Integrations;
