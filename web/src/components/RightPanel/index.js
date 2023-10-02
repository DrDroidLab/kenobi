import React from 'react';
import { Link } from 'react-router-dom';
import '../../../src/Layout.css';

const RightPanel = () => {
  return (
    <div className="rightPanel py-4">
      <div className="flex flex-col mb-10">
        <iframe
          width="100%"
          height="100%"
          src="https://www.loom.com/embed/79f5fa10f57f4227a78d2c98969400ff"
          title="YouTube video player"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          className="rounded"
        />
      </div>
      <div>
        <h5 className="font-medium text-purple-700 text-base text-voilet-600">
          Demo to setup your first monitor
        </h5>
        <hr />
        <ul className="text-gray-500 text-sm	my-6">
          <div className="mb-6">
            <ul>
              <li>
                - &nbsp;
                <a
                  href="https://www.loom.com/share/79f5fa10f57f4227a78d2c98969400ff"
                  className="underline"
                  target="_blank"
                >
                  Check out our demo video
                </a>
              </li>
              <li>
                - &nbsp;
                <a
                  href="https://docs.drdroid.io/reference/events"
                  className="underline"
                  target="_blank"
                >
                  Send sample events
                </a>
              </li>
              <li>
                - &nbsp;
                <a className="underline" href="/monitors/create">
                  Create your first monitor
                </a>
              </li>
              <li>
                - &nbsp;Setup alerts on your slack channel <br /> &nbsp;&nbsp;&nbsp;(
                <a href="https://youtu.be/6NJuntZSJVA" className="underline" target="_blank">
                  Create a slack webhook URL
                </a>
                )
              </li>
              <li>-&nbsp; Setup email / Slack triggers</li>
            </ul>
          </div>
        </ul>
      </div>
      <hr />
      <div className="my-5">
        <a
          className="font-medium text-purple-700 text-base text-voilet-600 cursor-pointer underline"
          href="https://docs.drdroid.io"
          target="_blank"
        >
          Documentation
        </a>
      </div>
      <hr />
      <div>
        <ul className="text-gray-500 text-sm	my-6">
          <li> Have questions or feedback? Message us and share your inputs</li>
        </ul>
      </div>
    </div>
  );
};

export default RightPanel;
