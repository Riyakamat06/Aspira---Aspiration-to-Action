
import React from "react";
import "./Components.css";

const ResourceList = ({ resources = [] }) => {
  if (!resources.length) {
    return (
      <div className="resource-list">
        <h3>📚 Learning Resources</h3>
        <p>No resources available yet. Check back soon!</p>
      </div>
    );
  }

  return (
    <div className="resource-list">
      <h3>📚 Recommended Learning Resources</h3>
      <p>Explore these resources to improve your skills.</p>

      <div className="resource-items">
        {resources.map((resource, index) => (
          <div className="resource-card" key={resource.id || index}>
            <h4>{resource.title || "Learning Resource"}</h4>

            {resource.description && (
              <p>{resource.description}</p>
            )}

            {resource.type && (
              <span>{resource.type}</span>
            )}

            {resource.url && (
              <a
                href={resource.url}
                target="_blank"
                rel="noopener noreferrer"
              >
                Explore Resource ↗
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ResourceList;
